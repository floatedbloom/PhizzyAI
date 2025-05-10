import streamlit as st
from body_diagram import render_body_diagram
from chatbot import chatbot
import numpy as np
import asyncio

st.title("PhizzyAI")

render_body_diagram()

chatbot()