import streamlit as st
from body_diagram import render_body_diagram
from chatbot import chatbot

# Set page configuration
st.set_page_config(
    page_title="Phizzy - Your Virtual Physical Therapist",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Add a themed header
st.markdown(
    """
    <style>
    body {
        background-color: #f0f8ff;
        font-family: 'Arial', sans-serif;
    }
    .header {
        text-align: center;
        font-size: 3em;
        font-weight: bold;
        color: #1abc9c;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.2);
        margin-bottom: 20px;
    }
    .subheader {
        text-align: center;
        font-size: 1.2em;
        color: #34495e;
        margin-bottom: 40px;
    }
    </style>
    <div class="header">Welcome to PhizzyAI</div>
    <div class="subheader">Your Virtual Physical Therapist</div>
    """,
    unsafe_allow_html=True,
)

# Create a two-column layout with reduced spacing
col1, col2 = st.columns([0.5, 1], gap="medium")

# Render body diagram in the first column
with col1:
    st.header("Interactive Diagram")
    render_body_diagram()

# Render chatbot in the second column
with col2:
    st.header("Chat with Phizzy")
    chatbot()