import os
import streamlit as st
from google import genai
from google.genai import types

class InterviewEvaluator:
    def __init__(self):
        # Look in Streamlit secrets first, then environment variables
        api_key = None
        try:
            if "GEMINI_API_KEY" in st.secrets:
                api_key = st.secrets["GEMINI_API_KEY"]
        except Exception:
            pass
            
        if not api_key:
            api_key = os.environ.get("GEMINI_API_KEY")
            
        self.client = genai.Client(api_key=api_key)
        
        self.system_prompt = """
        You are an expert technical recruiter and interviewer.
        Review the provided interview transcript between an AI Interviewer and a Candidate.
        Generate a detailed performance report formatted exactly like this in Markdown:
        
        ## Performance Evaluation Report
        **Overall Score:** [Score out of 100]
        
        ### Strengths
        - [Key strength 1]
        - [Key strength 2]
        
        ### Areas for Improvement
        - [Area 1]
        - [Area 2]
        
        ### Detailed Technical Breakdown
        [Provide a concise, professional assessment of the candidate's technical skills, code quality, or conceptual answers demonstrated in the transcript.]
        """

    def evaluate_interview(self, messages) -> str:
        transcript = "\n".join([f"{msg['role'].capitalize()}: {msg['content']}" for msg in messages])
        prompt = f"Please evaluate the following interview transcript based on your system instructions:\n\n{transcript}"
        
        response = self.client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=self.system_prompt,
                temperature=0.3
            )
        )
        return response.text