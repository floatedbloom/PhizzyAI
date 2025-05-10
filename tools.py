from openai import AsyncOpenAI
from dotenv import load_dotenv
import os
import speech_recognition as sr
import streamlit as st
import json
from typing import Dict, Any, List, Optional, Tuple, Union
from mcp import MCPServer, MuscleType
import asyncio

load_dotenv()
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
mcp_server = MCPServer()

async def chat_callback(message: str) -> None:
    """Send message to chat - will be captured by the Streamlit app"""
    st.session_state.setdefault("mcp_messages", [])
    st.session_state.mcp_messages.append(message)

# Set up the MCP server's chat callback
mcp_server.set_chat_callback(chat_callback)

async def generate_chat_analysis(
    user_input: str, 
    chat_history: List[Dict[str, str]] = None,
    body_json: str = None,
) -> Union[str, Tuple[str, dict]]:
    """
    Generate an analysis of user's physical health concerns.
    
    Args:
        user_input: The user's current message
        chat_history: Optional chat history for context
        body_json: Optional JSON string containing current body status
        
    Returns:
        If body_json is provided, returns a tuple with (display_response, parsed_json_response)
        Otherwise, returns just the text response
    """
    # Use chat history if provided, otherwise initialize empty
    if chat_history is None:
        chat_history = []
        
    # Define tools in the correct format for all system prompts
    tools = [
        {
            "type": "function",
            "function": {
                "name": "send_stretches",
                "description": "Send specific stretches for a muscle group",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "muscle": {
                            "type": "string",
                            "enum": [
                                "hands", "forearms", "biceps", "front-shoulders", "chest", 
                                "obliques", "abdominals", "quads", "calves", "triceps", 
                                "rear-shoulders", "traps", "traps-middle", "lats", 
                                "lowerback", "hamstrings", "glutes", "calves"
                            ],
                            "description": "The specific muscle group to get stretches for"
                        }
                    },
                    "required": ["muscle"]
                }
            }
        }
    ]
        
    # Create the appropriate system message based on whether body_json is provided
    if body_json:
        # Create system message with JSON structure instructions
        system_message = (
            "You are PhizzyAI, an advanced AI physical therapist. Your role is to analyze user-reported "
            "pain, discomfort, or physical issues and provide detailed, empathetic, and actionable advice. "
            "You are highly knowledgeable in anatomy, physical therapy techniques, and rehabilitation exercises. "
            "When a user describes their symptoms, you will:\n"
            "1. Identify the potential cause of the issue based on the symptoms described.\n"
            "2. Suggest specific stretches, exercises, or techniques to alleviate the pain or discomfort.\n"
            "3. Provide clear warnings if the symptoms described could indicate a serious condition that requires "
            "immediate medical attention.\n"
            "4. Always communicate in a professional, empathetic, and easy-to-understand manner.\n\n"
            f"User Input: {user_input}\n\n"
            f"preexisting json file structure: {body_json}\n\n"
            "You have access to the following tools:\n"
            "- send_stretches: Send specific stretches for a muscle group\n"
            "  Parameters: muscle (string) - one of: hands, forearms, biceps, front-shoulders, chest, obliques, abdominals, "
            "quads, calves, triceps, rear-shoulders, traps, traps-middle, lats, lowerback, hamstrings, glutes, calves\n\n"
            "Your response should include:\n"
            "- A brief analysis of the symptoms.\n"
            "- Suggested actions or exercises.\n"
            "- Any necessary warnings or advice to seek medical attention if applicable.\n"
            "If you recommend stretches for specific muscles, use the send_stretches tool to provide links.\n\n"
            "Create a JSON object with the following structure:\n"
            "{\n"
            "    \"muscle_group_name\": {\n"
            "        \"pain_points\": [\"symptom1\", \"symptom2\", ...],\n"
            "        \"pain_level\": \"number from 1-10\",\n"
            "        \"warnings\": [\"warning1\", \"warning2\", ...],\n"
            "        \"exercises\": [\"exercise1\", \"exercise2\", ...]\n"
            "    },\n"
            "    \"actual query response\": [\"your complete response to user in natural language\"]\n"
            "}\n"
            "Make sure to use the correct muscle group names as keys. "
            "The muscle groups are: right trap, right shoulder, right chest, right bicep, right forearm, "
            "right oblique, left trap, left shoulder, left chest, left bicep, left forearm, left oblique, "
            "abs, groin, right thigh, left thigh, right calf, left calf.\n"
            "The pain level should be a number from 1 to 10 as a string, where 1 is minimal pain and 10 is extreme pain. "
            "The pain_points should describe the specific symptoms (e.g., stiffness, soreness, sharp pain). "
            "The exercises should be specific to the muscle groups mentioned. "
            "The warnings should be clear and concise, indicating if the user should seek medical attention.\n"
            "Please provide a detailed and informative response."
        )
        
        # Use o4-mini for JSON structure responses
        try:
            # Format chat history for API call
            formatted_messages = []
            
            # Add system message first
            formatted_messages.append({"role": "system", "content": system_message})
            
            # Add previous conversation history (excluding the latest user message)
            for message in chat_history:
                # Skip tool-generated messages when sending to the model
                if "Stretches for" not in message.get("content", ""):
                    formatted_messages.append({
                        "role": message["role"],
                        "content": message["content"]
                    })
            
            # Add current user message
            formatted_messages.append({"role": "user", "content": user_input})
            
            # Make API call with tools included
            response = await client.chat.completions.create(
                model='gpt-4o',
                messages=formatted_messages,
                tools=tools,
                tool_choice="auto",
                response_format={"type": "json_object"},
            )
            
            response_message = response.choices[0].message
            response_text = response_message.content or "{}"
            
            # Process tool calls if they exist
            if hasattr(response_message, 'tool_calls') and response_message.tool_calls:
                await process_tool_calls(response_message.tool_calls)
            
            # Try to parse as JSON
            try:
                response_json = json.loads(response_text)
                
                # Extract and handle "actual query response"
                actual_response = response_json.pop("actual query response", ["No response found"])
                if isinstance(actual_response, list):
                    actual_response = "\n".join(actual_response)
                
                # Return both display text and the JSON data
                return actual_response, response_json
                
            except json.JSONDecodeError:
                # If JSON parsing fails, return raw response
                return response_text, {}
                
        except Exception as e:
            print(f"Error in generate_chat_analysis json mode: {e}")
            return f"I'm sorry, there was an error processing your request. Please try again.", {}
    
    else:
        # Use chat-based approach with tools for regular chat mode
        system_message = (
            "You are PhizzyAI, an advanced AI physical therapist. Your role is to analyze user-reported "
            "pain, discomfort, or physical issues and provide detailed, empathetic, and actionable advice. "
            "You are highly knowledgeable in anatomy, physical therapy techniques, and rehabilitation exercises. "
            "When a user describes their symptoms, you will:\n"
            "1. Identify the potential cause of the issue based on the symptoms described.\n"
            "2. Suggest specific stretches, exercises, or techniques to alleviate the pain or discomfort.\n"
            "3. Provide clear warnings if the symptoms described could indicate a serious condition that requires "
            "immediate medical attention.\n"
            "4. Always communicate in a professional, empathetic, and easy-to-understand manner.\n\n"
            "You have access to the following tools:\n"
            "- send_stretches: Send specific stretches for a muscle group\n"
            "  Parameters: muscle (string) - one of: hands, forearms, biceps, front-shoulders, chest, obliques, abdominals, "
            "quads, calves, triceps, rear-shoulders, traps, traps-middle, lats, lowerback, hamstrings, glutes, calves\n\n"
            "Your response should include:\n"
            "- A brief analysis of the symptoms.\n"
            "- Suggested actions or exercises.\n"
            "- Any necessary warnings or advice to seek medical attention if applicable.\n"
            "If you recommend stretches for specific muscles, use the send_stretches tool to provide links."
        )
        
        try:
            # Format chat history for API call
            formatted_messages = []
            
            # Add system message first
            formatted_messages.append({"role": "system", "content": system_message})
            
            # Add previous conversation history (excluding the latest user message)
            for message in chat_history:
                # Skip tool-generated messages when sending to the model
                if "Stretches for" not in message.get("content", ""):
                    formatted_messages.append({
                        "role": message["role"],
                        "content": message["content"]
                    })
            
            # Add current user message
            formatted_messages.append({"role": "user", "content": user_input})
            
            # Make API call with conversation history
            response = await client.chat.completions.create(
                model='gpt-4o',
                messages=formatted_messages,
                tools=tools,
                tool_choice="auto",
            )
            
            # Process response for tool calls
            response_message = response.choices[0].message
            
            if hasattr(response_message, 'tool_calls') and response_message.tool_calls:
                await process_tool_calls(response_message.tool_calls)
            
            # Return the content directly if available
            if response_message.content:
                return response_message.content
            
            # If no content but tool calls were made, get a follow-up response
            if hasattr(response_message, 'tool_calls') and response_message.tool_calls:
                # Add tool call info
                formatted_messages.append({
                    'role': 'assistant',
                    'content': None,
                    'tool_calls': response_message.tool_calls
                })
                
                # Add tool call results
                for tool_call in response_message.tool_calls:
                    formatted_messages.append({
                        'role': 'tool',
                        'tool_call_id': tool_call.id,
                        'content': "Tools processed successfully. Stretches have been sent to the user."
                    })
                
                fallback_response = await client.chat.completions.create(
                    model='gpt-4o',
                    messages=formatted_messages,
                )
                
                return fallback_response.choices[0].message.content
            
            # If all else fails
            return "I've analyzed your input and sent appropriate resources. Is there anything specific you'd like to know more about?"
        
        except Exception as e:
            print(f"Error in generate_chat_analysis: {e}")
            return f"I'm sorry, there was an error processing your request. Please try again."

async def process_tool_calls(tool_calls):
    """Process tool calls from the LLM response"""
    for tool_call in tool_calls:
        function_name = tool_call.function.name
        function_args = json.loads(tool_call.function.arguments)
        
        if function_name == "send_stretches":
            muscle = function_args.get("muscle")
            if muscle:
                await mcp_server.send_stretches(muscle)
    
    # Wait briefly to ensure tool calls are processed
    await asyncio.sleep(0.5)

def get_audio_input():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.write("Listening... Please speak now 🗣️")
        try:
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source, phrase_time_limit=10)
            st.write("Processing your input...")
            text = recognizer.recognize_google(audio)
            return text
        except sr.UnknownValueError:
            st.write("Sorry, I could not understand the audio.")
            return ""
        except sr.RequestError as e:
            st.write(f"Could not request results; {e}")
            return ""