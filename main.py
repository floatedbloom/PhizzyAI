import streamlit as st
from body_diagram import render_body_diagram
import numpy as np
import asyncio
from tools import generate_chat_analysis, get_audio_input


st.title("PhizzyAI")

st.write("Placeholder for the body diagram")

def chatbot():
    chatbox = st.container(height=800)
    if st.button("Speak your query"):
        prompt = get_audio_input()
        if prompt:
            with chatbox.chat_message("user"):
                st.markdown(prompt)
            with st.spinner("Analyzing your input..."):
                response = asyncio.run(generate_chat_analysis(prompt))
            with chatbox.chat_message("assistant"):
                st.markdown(response)

chatbot()