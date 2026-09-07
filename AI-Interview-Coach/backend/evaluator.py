import os
import streamlit as st
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

class InterviewEvaluator:
    def __init__(self):
        api_key = st.secrets["AQ.Ab8RN6JkgptquKCQfYDxa3wSXVPBJTZpwBBruMDTEaWyRS39ZA"] if "AQ.Ab8RN6JkgptquKCQfYDxa3wSXVPBJTZpwBBruMDTEaWyRS39ZA" in st.secrets else os.environ.get("AQ.Ab8RN6JkgptquKCQfYDxa3wSXVPBJTZpwBBruMDTEaWyRS39ZA")
        self.client = genai.Client(api_key=api_key)
        
        self.system_prompt = """
        You are an expert technical recruiter and interviewer.
        Review the provided interview transcript between an AI Interviewer and a Candidate.
        Generate a detailed performance report formatted exactly like this in Markdown:"""