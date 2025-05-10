from openai import AsyncOpenAI
from dotenv import load_dotenv
import os
import speech_recognition as sr
import streamlit as st
import json
from typing import Dict, Any, List, Optional
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

async def generate_chat_analysis(user_input: str, chat_history: List[Dict[str, str]] = None) -> str:
    # Use chat history if provided, otherwise initialize empty
    if chat_history is None:
        chat_history = []
    
    # Create system message with instructions
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
    
    # Define tools in the correct format
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
    
    try:
        # Format chat history for API call
        formatted_messages = []
        
        # Add system message first
        formatted_messages.append({"role": "system", "content": system_message})
        
        # Add previous conversation history (excluding the latest user message)
        for message in chat_history:
            # Skip tool-generated messages when sending to the model
            if "send_stretches" not in message.get("content", ""):
                formatted_messages.append({
                    "role": message["role"],
                    "content": message["content"]
                })
        
        # Add current user message
        formatted_messages.append({"role": "user", "content": user_input})
        
        # Make API call with conversation history
        response = await client.chat.completions.create(
            model='gpt-4.1-nano',
            messages=formatted_messages,
            tools=tools,
            tool_choice="auto",
        )
        
        # Process response for tool calls
        tool_calls_made = False
        response_message = response.choices[0].message
        
        if hasattr(response_message, 'tool_calls') and response_message.tool_calls:
            tool_calls_made = True
            for tool_call in response_message.tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)
                
                if function_name == "send_stretches":
                    muscle = function_args.get("muscle")
                    if muscle:
                        await mcp_server.send_stretches(muscle)
        
        # Wait to ensure tool calls are processed
        await asyncio.sleep(0.5)
        
        # Return the content directly if available
        if response_message.content:
            return response_message.content
        
        # If no content but tool calls were made, get a follow-up response
        if tool_calls_made:
            # Add tool call info
            formatted_messages.append({
                'role': 'system', 
                'content': "Tool calls for stretches have been made. Please provide a comprehensive response to the user's question."
            })
            
            fallback_response = await client.chat.completions.create(
                model='gpt-4.1-nano',
                messages=formatted_messages,
                temperature=0.7,
            )
            
            return fallback_response.choices[0].message.content
        
        # If all else fails
        return "I've analyzed your input and sent appropriate resources. Is there anything specific you'd like to know more about?"
    
    except Exception as e:
        print(f"Error in generate_chat_analysis: {e}")
        return f"I'm sorry, there was an error processing your request. Please try again."

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