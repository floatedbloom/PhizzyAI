import streamlit as st
from body_diagram import render_body_diagram
import numpy as np
import asyncio
from tools import generate_chat_analysis


st.title("PhizzyAI")

st.write("Placeholder for the body diagram")

prompt = "my left oblique hurts whenever I bend my neck downwards to the right"

def chatbot():
    chatbox = st.container(height=800)
    if prompt := st.chat_input("Enter query here"):
        with chatbox.chat_message("user"):
            st.markdown(prompt)
        with st.spinner("Analyzing your input..."):
            response = asyncio.run(generate_chat_analysis(prompt))
        with chatbox.chat_message("assistant"):
            st.markdown(response)


# Call the function to render the page
chatbot()