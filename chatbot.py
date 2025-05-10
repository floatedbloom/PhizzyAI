import streamlit as st
import asyncio
import speech_recognition as sr
import os
from tools import generate_chat_analysis, get_audio_input

def chatbot():
    # Initialize chat history if not exists
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    # Initialize MCP messages if not exists
    st.session_state.setdefault("mcp_messages", [])
    
    # Initialize processing flags
    if "processing_text" not in st.session_state:
        st.session_state.processing_text = False
    if "processing_voice" not in st.session_state:
        st.session_state.processing_voice = False
    
    # Handle form submission for text input
    def handle_text_submit():
        if st.session_state.text_query and not st.session_state.processing_text:
            # Get the text from the session state
            prompt = st.session_state.text_query
            
            # Reset the input field
            st.session_state.text_query = ""
            
            # Set processing flag
            st.session_state.processing_text = True
            
            # Add user message to history
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            
            # Indicate reprocessing needed
            st.session_state.needs_rerun = True
    
    # Handle text processing outside form to prevent infinite loops
    if st.session_state.get("needs_rerun", False) and st.session_state.processing_text:
        # Reset flag
        st.session_state.needs_rerun = False
        
        # Get the latest user message
        latest_user_message = next((msg["content"] for msg in reversed(st.session_state.chat_history) 
                                   if msg["role"] == "user"), None)
        
        if latest_user_message:
            with st.spinner("Analyzing your input..."):
                # Pass chat history for context
                response = asyncio.run(generate_chat_analysis(
                    latest_user_message, 
                    chat_history=st.session_state.chat_history[:-1]  # Exclude the latest message
                ))
            
            # Add assistant message to history
            st.session_state.chat_history.append({"role": "assistant", "content": response})
        
        # Reset flag
        st.session_state.processing_text = False
        st.rerun()
    
    chatbox = st.container(height=800)
    
    # Display all messages from chat history
    for message in st.session_state.chat_history:
        role = message["role"]
        content = message["content"]
        with chatbox.chat_message(role):
            st.markdown(content)
    
    # Display any new MCP messages
    if st.session_state.mcp_messages:
        for message in st.session_state.mcp_messages:
            # Add tool message to history
            st.session_state.chat_history.append({"role": "assistant", "content": message})
            
            # Display tool message
            with chatbox.chat_message("assistant"):
                st.markdown(message)
        
        # Clear MCP messages after adding to history and displaying
        st.session_state.mcp_messages = []
        st.rerun()
    
    # Text query handling with form
    with st.form(key="query_form", clear_on_submit=True):
        text_input = st.text_input("Text Query:", key="text_query")
        submit_button = st.form_submit_button("Send", on_click=handle_text_submit)
    
    # Voice query handling
    if st.button("Spoken Query 🎤") and not st.session_state.processing_voice:
        st.session_state.processing_voice = True
        
        prompt = get_audio_input()
        if prompt:
            # Add user message to history immediately
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            
            # Force a rerun to display the user message first
            st.rerun()
    
    # Process voice response after user message is displayed
    if st.session_state.processing_voice and st.session_state.chat_history:
        latest_user_message = next((msg["content"] for msg in reversed(st.session_state.chat_history) 
                                    if msg["role"] == "user"), None)
        
        if latest_user_message:
            with st.spinner("Analyzing your input..."):
                # Pass chat history for context
                response = asyncio.run(generate_chat_analysis(
                    latest_user_message,
                    chat_history=st.session_state.chat_history[:-1]  # Exclude the latest message
                ))
            
            # Add assistant message to history
            st.session_state.chat_history.append({"role": "assistant", "content": response})
        
        # Reset flag
        st.session_state.processing_voice = False
        st.rerun()