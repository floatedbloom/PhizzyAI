import streamlit as st
from tools import generate_chat_analysis, get_audio_input
import asyncio
import os
import json

def chatbot():
    # Load body.json
    json_path = "body.json"
    if os.path.exists(json_path):
        with open(json_path, "r") as f:
            try:
                body_data = json.load(f)
            except json.JSONDecodeError:
                body_data = {}
    else:
        body_data = {}
    
    # Convert to string for passing to the LLM
    body_json = json.dumps(body_data)
    
    chatbox = st.container(height=800)
    prompt = st.text_input("Text Query:")
    if prompt:
        with chatbox.chat_message("user"):
            st.markdown(prompt)
        with st.spinner("Analyzing your input..."):
            response = asyncio.run(generate_chat_analysis(prompt, body_json=body_json))
            try:
                # If response is a tuple (meaning it contains the display_text and JSON data)
                if isinstance(response, tuple) and len(response) == 2:
                    actual_response, response_json = response
                    
                    # Update existing JSON data with new info from response
                    for muscle_group, info in response_json.items():
                        if muscle_group in body_data:
                            # Update existing muscle group data
                            body_data[muscle_group].update(info)
                        else:
                            # Add new muscle group data
                            body_data[muscle_group] = info
                    
                    # Save the updated JSON to file
                    with open(json_path, "w") as f:
                        json.dump(body_data, f, indent=2)
                else:
                    actual_response = response
                    
            except Exception as e:
                st.error(f"Error processing response: {e}")
                actual_response = response if isinstance(response, str) else str(response)
                
        with chatbox.chat_message("assistant"):
            st.markdown(actual_response)
    
    if st.button("Spoken Query 🎤"):
        prompt = get_audio_input()
        if prompt:
            with chatbox.chat_message("user"):
                st.markdown(prompt)
            with st.spinner("Analyzing your input..."):
                response = asyncio.run(generate_chat_analysis(prompt, body_json=body_json))
                try:
                    # If response is a tuple (meaning it contains the display_text and JSON data)
                    if isinstance(response, tuple) and len(response) == 2:
                        actual_response, response_json = response
                        
                        # Update existing JSON data with new info from response
                        for muscle_group, info in response_json.items():
                            if muscle_group in body_data:
                                # Update existing muscle group data
                                body_data[muscle_group].update(info)
                            else:
                                # Add new muscle group data
                                body_data[muscle_group] = info
                        
                        # Save the updated JSON to file
                        with open(json_path, "w") as f:
                            json.dump(body_data, f, indent=2)
                    else:
                        actual_response = response
                        
                except Exception as e:
                    st.error(f"Error processing response: {e}")
                    actual_response = response if isinstance(response, str) else str(response)
                    
            with chatbox.chat_message("assistant"):
                st.markdown(actual_response)

if __name__ == "__main__":
    st.title("PhizzyAI - Your Personal Physical Therapy Assistant")
    chatbot()