import os
import streamlit as st
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

class InterviewerEngine:
    def __init__(self, topic="Technical", difficulty="Intermediate"):
        api_key = st.secrets["GEMINI_API_KEY"] if "GEMINI_API_KEY" in st.secrets else os.environ.get("GEMINI_API_KEY")
        self.client = genai.Client(api_key=api_key)
        
        self.system_prompt = f"""
        You are a senior engineering manager conducting a {difficulty}-level {topic} interview.
        Rules:
        1. Ask ONLY ONE question at a time.
        2. Wait for the user's answer before proceeding.
        3. If the user provides code, you MUST ask them to explain the Time and Space Complexity (Big-O).
        4. If {difficulty} is "Advanced" or "FAANG/Hackathon Level", ask complex questions involving scalability, graph algorithms, or fine-grained locking strategies where appropriate.
        5. NEVER provide the full correct answer yourself. 
        6. Keep the tone professional, encouraging, but concise.
        """
        
        self.chat = self.client.chats.create(
            model='gemini-3.6-flash',
            config=types.GenerateContentConfig(
                system_instruction=self.system_prompt,
                temperature=0.7 
            )
        )
        
    from google.genai.errors import ServerError, ClientError

class AIEngine:
    def __init__(self, api_key, topic, difficulty):
        self.client = genai.Client(api_key=api_key)
        self.model = 'gemini-2.5-flash' # or gemini-3.6-flash depending on your working setup
        
        # Initialize chat session
        self.chat = self.client.chats.create(
            model=self.model,
            config=types.GenerateContentConfig(
                system_instruction=f"You are a strict technical interviewer conducting a mock interview on {topic} at a {difficulty} level.",
                temperature=0.7
            )
        )

    def send_message(self, message):
        try:
            response = self.chat.send_message(message)
            return response.text
        except ServerError:
            return "⚠️ **AI Service Temporarily Busy:** Google's Gemini servers are experiencing a brief hiccup. Please try sending your message again in a few seconds."
        except Exception as e:
            return f"⚠️ An unexpected error occurred: {str(e)}"