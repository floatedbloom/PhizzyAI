import asyncio
import json
from typing import Dict, List, Literal, Optional, Any, Callable, Awaitable
from muscle_stretch_summaries import muscle_stretch_summaries

MuscleStatus = Literal["green", "orange", "red"]
MuscleType = Literal[
    "hands", "forearms", "biceps", "front-shoulders", "chest", 
    "obliques", "abdominals", "quads", "calves", "triceps", 
    "rear-shoulders", "traps", "traps-middle", "lats", 
    "lowerback", "hamstrings", "glutes", "calves",
]

class MCPServer:
    def __init__(self, host: str = "localhost", port: int = 8000):
        self.host = host
        self.port = port
        self.resources: Dict[str, Callable[..., Awaitable[Any]]] = {}
        self.tools: Dict[str, Callable[..., Awaitable[Any]]] = {}
        self.chat_callback: Optional[Callable[[str], Awaitable[None]]] = None
        
        # Register resources and tools
        self._register_resources()
        self._register_tools()
    
    def _register_resources(self) -> None:
        """Register resource handlers"""
        self.resources["fetch_parts"] = self.fetch_parts
    
    def _register_tools(self) -> None:
        """Register tool handlers"""
        self.tools["update_status"] = self.update_status
        self.tools["send_stretches"] = self.send_stretches
    
    def set_chat_callback(self, callback: Callable[[str], Awaitable[None]]) -> None:
        """Set callback for sending messages to chat"""
        self.chat_callback = callback
    
    async def fetch_parts(self) -> Dict[MuscleType, MuscleStatus]:
        """
        Resource to fetch the status of all body muscles.
        This is a placeholder and should be implemented later.
        """
        # Placeholder - to be implemented
        raise NotImplementedError("fetch_parts is not implemented yet")
    
    async def update_status(self, muscles: Dict[MuscleType, MuscleStatus]) -> bool:
        """
        Tool to update the status of a list of body muscles.
        This is a placeholder and should be implemented later.
        """
        # Placeholder - to be implemented
        raise NotImplementedError("update_status is not implemented yet")
    
    async def send_stretches(self, muscle: MuscleType) -> bool:
        """
        Tool to send stretches for a specific part of the muscles.
        Sends a URL to the chat with stretch summaries and visual demonstrations.
        """
        if not self.chat_callback:
            return False
        
        muscle_codename = muscle.replace("-", "_")
        
        # URLs for demonstration views
        main_url = f"https://musclewiki.com/stretches/male/{muscle_codename}"
        
        # Get stretches summary from the muscle_stretch_summaries
        stretches_summary = muscle_stretch_summaries.get(muscle, f"No specific stretches found for {muscle}")
        
        # Create message with dark theme for better contrast and without iframe (due to X-Frame-Options restrictions)
        message = f"""
<div style="background-color: #1e3d2a; border-left: 4px solid #28a745; padding: 15px; margin-bottom: 15px; border-radius: 4px;">
    <div style="display: flex; align-items: top;">
        <div style="color: #28a745; font-size: 24px; margin-right: 10px;">
            <i class="fas fa-info-circle"></i> <!-- Font Awesome info icon -->
        </div>
        <div>
            <strong style="color: #28a745;">Stretches for {muscle}</strong>
            <div style="color: #ffffff;">{stretches_summary}</div>
        </div>
    </div>
</div>

<div style="text-align: center; margin-top: 15px; margin-bottom: 20px;">
    <a href="{main_url}" target="_blank" style="display: inline-block; background-color: #28a745; color: white; text-decoration: none; padding: 10px 20px; border-radius: 4px; font-weight: bold;">
        <i class="fas fa-external-link-alt"></i> View Stretches on MuscleWiki
    </a>
    <p style="margin-top: 10px; font-size: 0.8em; color: #666;">
        Note: The website cannot be embedded due to security restrictions.
    </p>
</div>
"""
        
        await self.chat_callback(message)
        return True
    
    async def handle_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming requests and route them to appropriate handlers"""
        try:
            request_type = request_data.get("type", "")
            action = request_data.get("action", "")
            params = request_data.get("params", {})
            
            if request_type == "resource" and action in self.resources:
                result = await self.resources[action](**params)
                return {"status": "success", "data": result}
            elif request_type == "tool" and action in self.tools:
                result = await self.tools[action](**params)
                return {"status": "success", "data": result}
            else:
                return {"status": "error", "message": f"Unknown {request_type} or action: {action}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def start_server(self) -> None:
        """Start the MCP server"""
        server = await asyncio.start_server(
            self._handle_client, self.host, self.port
        )
        
        async with server:
            print(f"MCP Server running on {self.host}:{self.port}")
            await server.serve_forever()
    
    async def _handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        """Handle client connection"""
        addr = writer.get_extra_info('peername')
        print(f"Connected by {addr}")
        
        while True:
            data = await reader.readline()
            if not data:
                break
                
            try:
                request = json.loads(data.decode())
                response = await self.handle_request(request)
                writer.write(json.dumps(response).encode() + b'\n')
                await writer.drain()
            except json.JSONDecodeError:
                writer.write(json.dumps({"status": "error", "message": "Invalid JSON"}).encode() + b'\n')
                await writer.drain()
        
        print(f"Disconnected from {addr}")
        writer.close()

async def example_chat_callback(message: str) -> None:
    """Example callback for sending messages to chat"""
    print(f"CHAT: {message}")

async def main() -> None:
    """Main function to run the MCP server"""
    server = MCPServer()
    server.set_chat_callback(example_chat_callback)
    await server.start_server()

if __name__ == "__main__":
    asyncio.run(main())
