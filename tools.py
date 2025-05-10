from openai import AsyncOpenAI
from dotenv import load_dotenv
import os
import speech_recognition as sr
import streamlit as st
import json
from typing import Dict, Any, List, Optional
from mcp import MCPServer, MuscleType

load_dotenv()
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
mcp_server = MCPServer()

async def chat_callback(message: str) -> None:
    """Send message to chat - will be captured by the Streamlit app"""
    st.session_state.setdefault("mcp_messages", [])
    st.session_state.mcp_messages.append(message)

# Set up the MCP server's chat callback
mcp_server.set_chat_callback(chat_callback)

async def generate_chat_analysis(user_input: str) -> str:
    prompt_text = (
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
        f"User Input: {user_input}\n\n"
        "Your response should include:\n"
        "- A brief analysis of the symptoms.\n"
        "- Suggested actions or exercises.\n"
        "- Any necessary warnings or advice to seek medical attention if applicable.\n"
        "If you recommend stretches for specific muscles, use the send_stretches tool to provide links."
    )
    
    tools = [
        {
            "type": "function",
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
    ]
    
    # First call: Allow the model to use tools
    content = [{"type": "input_text", "text": prompt_text}]
    messages = [{'role': 'user', 'content': content}]
    
    response = await client.responses.create(
        model='gpt-4.1-nano',
        input=messages,
        tools=tools,
        tool_choice="auto",
    )
    
    # Process any tool calls
    tool_calls_made = False
    for item in response.output:
        if hasattr(item, 'type') and item.type == "function_call":
            tool_calls_made = True
            function_name = item.name
            function_args = json.loads(item.arguments)
            
            if function_name == "send_stretches":
                muscle = function_args.get("muscle")
                if muscle:
                    await mcp_server.send_stretches(muscle)
    
    # Second call: Force a text response
    # Add any tool calls to the conversation history
    conversation = [
        {'role': 'user', 'content': user_input}
    ]
    
    if tool_calls_made:
        # Add a system message to inform the model about tool calls
        conversation.append({
            'role': 'system', 
            'content': "Function calls have been processed. Please provide a comprehensive response to the user's question about their symptoms."
        })
    
    # Get a text response
    text_response = await client.chat.completions.create(
        model='gpt-4.1-nano',
        messages=conversation,
        temperature=0.7,
    )
    
    return text_response.choices[0].message.content

def get_audio_input():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.write("Listening... Please speak now.")
        try:
            audio = recognizer.listen(source, phrase_time_limit=5000)
            st.write("Processing your input...")
            return recognizer.recognize_google(audio)
        except sr.UnknownValueError:
            st.write("Sorry, I could not understand the audio.")
            return ""
        except sr.RequestError as e:
            st.write(f"Could not request results; {e}")
            return ""