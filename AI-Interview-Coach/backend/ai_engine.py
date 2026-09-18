import os
from google import genai
from google.genai import types
from google.genai.errors import ServerError, ClientError

class InterviewerEngine:
    def __init__(self, api_key=None, topic="Technical", difficulty="Beginner"):
        # Fallback to environment or secrets if not passed directly
        if not api_key:
            api_key = os.environ.get("GEMINI_API_KEY")
            
        if not api_key:
            raise ValueError("GEMINI_API_KEY is missing. Please check your Streamlit Secrets.")
            
        self.client = genai.Client(api_key=api_key)
        self.model = 'gemini-2.5-flash'
        
        self.chat = self.client.chats.create(
            model=self.model,
            config=types.GenerateContentConfig(
                system_instruction=f"You are a professional technical interviewer conducting a mock interview on {topic} at a {difficulty} tier level. Ask focused questions one by one and evaluate the user's technical responses.",
                temperature=0.7
            )
        )

    def send_message(self, message):
        try:
            response = self.chat.send_message(message)
            return response.text
        except ServerError:
            return "⚠️ **AI Service Temporarily Busy:** Google's Gemini servers are experiencing a brief hiccup. Please try sending your message again in a few seconds."
        except ClientError:
            return "⚠️ **API Authorization Error:** Please verify that your `GEMINI_API_KEY` is active and correctly configured in Streamlit Secrets."
        except Exception as e:
            return f"⚠️ An unexpected error occurred: {str(e)}"