import streamlit as st
import numpy as np
import asyncio
from openai import AsyncOpenAI
from dotenv import load_dotenv
import os
import speech_recognition as sr
import json

load_dotenv()
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def generate_chat_analysis(user_input: str, json: str) -> str:
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
        f"User Input: {user_input}\n\n"
        f"preexisting json file structure: {json}"
        "Your response should include:\n"
        "- A brief analysis of the symptoms.\n"
        "- Suggested actions or exercises.\n"
        "- Any necessary warnings or advice to seek medical attention if applicable.\n"
        "Create a JSON object with the following structure:\n"
        "{\n 'pain points: [(names of the muscle groups)], 'pain level':[(pain level for each muscle group mapped by index)] ''"
        "'exercises': [(exercise name)], 'warnings': [(warning message)] }\n 'actual query response': [(actual query response)] }\n}"
        "Make sure to include the muscle groups in the response. "
        "The muscle groups are: right trap, right shoulder, right chest, right bicep, right forearm, "
        "right oblique, left trap, left shoulder, left chest, left bicep, left forearm, left oblique, "
        "abs, groin, right thigh, left thigh, right calf, left calf.\n"
        "The pain level should be a number from 1 to 10, where 1 is no pain and 10 is extreme pain. "
        "The exercises should be specific to the muscle groups mentioned. "
        "The warnings should be clear and concise, indicating if the user should seek medical attention.\n"
        "Please provide a detailed and informative response."
    )
    content = [{"type": "input_text", "text": prompt_text}]
    response = await client.responses.create(
        model='o4-mini',
        input=[{'role': 'user', 'content': content}],
    )
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

def chatbot():
    # Load body.json
    json_path = "body.json"
    if os.path.exists(json_path):
        with open(json_path, "r") as f:
            body_json = f.read()
    else:
        body_json = "{}"
    chatbox = st.container(height=800)
    prompt = st.text_input("Text Query:")
    if prompt:
        with chatbox.chat_message("user"):
            st.markdown(prompt)
        with st.spinner("Analyzing your input..."):
            response = asyncio.run(generate_chat_analysis(prompt, body_json))
        with chatbox.chat_message("assistant"):
            st.markdown(response)
    if st.button("Spoken Query 🎤"):
        prompt = get_audio_input()
        if prompt:
            with chatbox.chat_message("user"):
                st.markdown(prompt)
            with st.spinner("Analyzing your input..."):
                response = asyncio.run(generate_chat_analysis(prompt, body_json))
            with chatbox.chat_message("assistant"):
                st.markdown(response)