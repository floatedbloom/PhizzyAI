from openai import AsyncOpenAI
from dotenv import load_dotenv
import os
import speech_recognition as sr
import streamlit as st

load_dotenv()
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

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
    )
    return response.output_text

def get_audio_input():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.write("Listening... Please speak now.")
        try:
            audio = recognizer.listen(source, phrase_time_limit=500)
            st.write("Processing your input...")
            return recognizer.recognize_google(audio)
        except sr.UnknownValueError:
            st.write("Sorry, I could not understand the audio.")
            return ""
        except sr.RequestError as e:
            st.write(f"Could not request results; {e}")
            return ""