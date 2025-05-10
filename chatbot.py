import streamlit as st
import numpy as np
import asyncio
from openai import AsyncOpenAI
from dotenv import load_dotenv
import os
import speech_recognition as sr
from mcp import MCPServer, MuscleType, MuscleStatus
import json

load_dotenv()
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Initialize MCP server
mcp_server = MCPServer()

async def send_to_chat(message: str) -> None:
    """Callback for MCP server to send messages to chat"""
    if "chatbox" in st.session_state:
        with st.session_state.chatbox.chat_message("assistant"):
            st.markdown(message)

# Set the chat callback for MCP server
async def setup_mcp():
    mcp_server.set_chat_callback(send_to_chat)

async def generate_chat_analysis(user_input: str) -> str:
    # Define available tools
    tools = [
        {
            "type": "function",
            "function": {
                "name": "send_stretches",
                "description": "Send stretches for a specific part of the muscles",
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
                            "description": "The muscle group to get stretches for"
                        }
                    },
                    "required": ["muscle"]
                }
            }
        }
    ]

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
        "You have access to a tool to send stretches for specific muscle groups. If the user mentions specific "
        "muscle pain or asks about stretches for a particular area, use the send_stretches function to provide them "
        "with appropriate stretching resources.\n\n"
        f"User Input: {user_input}\n\n"
        "Your response should include:\n"
        "- A brief analysis of the symptoms.\n"
        "- Suggested actions or exercises.\n"
        "- Any necessary warnings or advice to seek medical attention if applicable.\n"
    )
    content = [{"type": "input_text", "text": prompt_text}]
    
    response = await client.responses.create(
        model='o4-mini',
        input=[{'role': 'user', 'content': content}],
        tools=tools,
    )
    
    # Process tool calls if any
    if hasattr(response, 'tool_calls') and response.tool_calls:
        for tool_call in response.tool_calls:
            if tool_call.function.name == "send_stretches":
                try:
                    args = json.loads(tool_call.function.arguments)
                    muscle = args.get("muscle")
                    if muscle:
                        await mcp_server.send_stretches(muscle)
                except Exception as e:
                    print(f"Error processing tool call: {e}")
    
    return response.output_text

def get_audio_input():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.write("Listening... Please speak now 🗣️")
        try:
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source, phrase_time_limit=5)
            st.write("Processing your input...")
            text = recognizer.recognize_google(audio)
            return text
        except sr.UnknownValueError:
            st.write("Sorry, I could not understand the audio.")
        except sr.RequestError as e:
            st.write(f"Could not request results; {e}")
    return ""

def start_listening():
    st.session_state.listening = True

def process_voice_input():
    if st.session_state.listening:
        text = get_audio_input()
        if text:
            st.session_state.voice_text = text
            st.session_state.process_voice = True
        st.session_state.listening = False
        # Force a rerun to show the results without opening a new tab
        st.rerun()

def chatbot():
    # Initialize session states
    if "chatbox" not in st.session_state:
        st.session_state.chatbox = st.container(height=800)
    if "listening" not in st.session_state:
        st.session_state.listening = False
    if "voice_text" not in st.session_state:
        st.session_state.voice_text = ""
    if "process_voice" not in st.session_state:
        st.session_state.process_voice = False
    
    chatbox = st.session_state.chatbox
    
    # Set up MCP server on first run
    if "mcp_setup" not in st.session_state:
        asyncio.run(setup_mcp())
        st.session_state.mcp_setup = True
    
    # Handle text input
    prompt = st.text_input("Text Query:")
    if prompt:
        with chatbox.chat_message("user"):
            st.markdown(prompt)
        with st.spinner("Analyzing your input..."):
            response = asyncio.run(generate_chat_analysis(prompt))
        with chatbox.chat_message("assistant"):
            st.markdown(response)
    
    # Handle voice input button
    st.button("Spoken Query 🎤", on_click=start_listening)
    
    # Process voice input if listening
    if st.session_state.listening:
        process_voice_input()
    
    # Process voice text if available
    if st.session_state.process_voice and st.session_state.voice_text:
        with chatbox.chat_message("user"):
            st.markdown(st.session_state.voice_text)
        with st.spinner("Analyzing your input..."):
            response = asyncio.run(generate_chat_analysis(st.session_state.voice_text))
        with chatbox.chat_message("assistant"):
            st.markdown(response)
        # Reset after processing
        st.session_state.voice_text = ""
        st.session_state.process_voice = False
