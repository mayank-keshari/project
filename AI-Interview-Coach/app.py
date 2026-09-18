import os
import re
import streamlit as st
import plotly.express as px
from backend.ai_engine import InterviewerEngine
from backend.evaluator import InterviewEvaluator
from backend.database import init_db, save_interview, get_history
from google.genai.errors import ServerError, ClientError

# Initialize the database on startup
init_db()

st.set_page_config(page_title="AI Interview Coach Pro", page_icon="🤖", layout="wide")

# Inject Custom High-End Glassmorphism CSS
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #0a0f1d, #1a2942, #1f4068);
        color: #ffffff;
    }
    .stChatMessage {
        background: rgba(255, 255, 255, 0.04);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border-radius: 16px;
        border: 1px solid rgba(255, 255, 255, 0.08);
        padding: 16px;
        margin-bottom: 12px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
    }
    [data-testid="stSidebar"] {
        background: rgba(10, 15, 29, 0.7) !important;
        backdrop-filter: blur(20px);
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }
    .login-container {
        max-width: 420px;
        margin: 80px auto;
        padding: 40px;
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 24px;
        box-shadow: 0 15px 35px rgba(0,0,0,0.5);
    }
    </style>
""", unsafe_allow_html=True)

# Helper function to get API key securely
def get_api_key():
    if "GEMINI_API_KEY" in st.secrets:
        return st.secrets["GEMINI_API_KEY"]
    return os.environ.get("GEMINI_API_KEY", "")

# Session state initialization for authentication
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "username" not in st.session_state:
    st.session_state.username = ""

# --- LOGIN SCREEN ---
if not st.session_state.authenticated:
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("""
            <div class="login-container">
                <h2 style="text-align: center; margin-bottom: 10px; font-weight: 700;">🚀 AI Coach Portal</h2>
                <p style="text-align: center; color: #94a3b8; font-size: 14px; margin-bottom: 30px;">
                    Sign in to launch your technical interview sandbox
                </p>
        """, unsafe_allow_html=True)
        
        user_input = st.text_input("Candidate Name", placeholder="e.g., Mayank Keshari")
        pass_input = st.text_input("Access PIN / Passkey", type="password", placeholder="••••••••")
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Enter Dashboard", type="primary", use_container_width=True):
            if user_input.strip():
                st.session_state.authenticated = True
                st.session_state.username = user_input.strip()
                st.rerun()
            else:
                st.error("Please enter a valid candidate name.")
        
        st.markdown("</div>", unsafe_allow_html=True)

# --- MAIN DASHBOARD (POST-LOGIN) ---
else:
    # Sidebar Controls
    with st.sidebar:
        st.markdown(f"### 👤 Profile: `{st.session_state.username}`")
        if st.button("Log Out", type="secondary", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.messages = []
            if "report" in st.session_state:
                del st.session_state.report
            if "engine" in st.session_state:
                del st.session_state.engine
            st.rerun()
            
        st.markdown("---")
        st.header("⚙️ Interview Setup")
        
        interview_type = st.selectbox(
            "Target Domain:",
            ["Technical", "Java", "Python", "DSA & Graph Algorithms", "SQL / DBMS", "HR"],
            key="type_select"
        )
        
        difficulty = st.select_slider(
            "Complexity Tier:",
            options=["Beginner", "Intermediate", "Advanced", "FAANG/Hackathon Level"]
        )
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔄 Restart Session", use_container_width=True):
            api_key = get_api_key()
            st.session_state.engine = InterviewerEngine(api_key=api_key, topic=interview_type, difficulty=difficulty)
            st.session_state.messages = [
                {"role": "assistant", "content": f"Session re-initialized for **{interview_type}** at **{difficulty}** tier. Let's begin!"}
            ]
            if "report" in st.session_state:
                del st.session_state.report
            st.rerun()

    # Ensure engine exists in session state
    if "engine" not in st.session_state:
        api_key = get_api_key()
        default_topic = st.session_state.get("type_select", "Technical")
        st.session_state.engine = InterviewerEngine(api_key=api_key, topic=default_topic, difficulty="Beginner")

    if "messages" not in st.session_state:
        st.session_state.messages = []
        st.session_state.messages.append({
            "role": "assistant", 
            "content": f"Welcome aboard, **{st.session_state.username}**! Let's begin your technical evaluation. Tell me about your background."
        })

    st.title("🤖 AI Interview Coach & Analytics")
    st.markdown(f"*Active Sandbox: Advanced Technical Screening Suite*")
    st.markdown("---")

    tab1, tab2, tab3 = st.tabs(["💬 Mock Interview", "📊 Performance Analytics", "📜 Evaluation Archive"])

    with tab1:
        if "report" in st.session_state:
            st.success("🎉 Evaluation Report Generated Successfully!")
            st.markdown(st.session_state.report)
            if st.button("Start New Practice Session"):
                del st.session_state.report
                st.session_state.messages = [{"role": "assistant", "content": "Ready for your next session. What topic shall we tackle?"}]
                st.rerun()
        else:
            for msg in st.session_state.messages:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])

            if prompt := st.chat_input("Enter your response or code solution..."):
                st.session_state.messages.append({"role": "user", "content": prompt})
                with st.chat_message("user"):
                    st.markdown(prompt)

                with st.chat_message("assistant"):
                    with st.spinner("Analyzing response & formatting next question..."):
                        try:
                            response = st.session_state.engine.send_message(prompt)
                        except ServerError:
                            response = "⚠️ **AI Service Temporarily Busy:** Google's Gemini servers are experiencing a brief hiccup. Please try sending your message again in a few seconds."
                        except ClientError:
                            response = "⚠️ **API Authorization Error:** Please verify that your `GEMINI_API_KEY` is correctly configured in Streamlit Secrets."
                        except Exception as e:
                            response = f"⚠️ An unexpected error occurred: {str(e)}"
                        
                        st.markdown(response)
                        
                st.session_state.messages.append({"role": "assistant", "content": response})

            st.markdown("---")
            col_action1, col_action2 = st.columns([4, 1])
            with col_action2:
                if st.button("🛑 Finish & Evaluate", type="primary", use_container_width=True):
                    if len(st.session_state.messages) > 2:
                        evaluator = InterviewEvaluator()
                        with st.spinner("Compiling technical assessment metrics and saving to database..."):
                            try:
                                report = evaluator.evaluate_interview(st.session_state.messages)
                                st.session_state.report = report
                                
                                match = re.search(r'\*\*Overall Score:\*\* (\d+)/100', report)
                                score = int(match.group(1)) if match else 0
                                
                                save_interview(st.session_state.get("type_select", "Technical"), score, report)
                                st.rerun()
                            except Exception as e:
                                st.error(f"Failed to generate evaluation report: {str(e)}")
                    else:
                        st.warning("Please interact with the interviewer before generating a report.")

    with tab2:
        st.header("📈 Progress & Skill Growth")
        df = get_history()
        
        if not df.empty:
            fig = px.line(
                df, 
                x="date", 
                y="score", 
                color="type",
                markers=True, 
                title="Historical Score Trajectory", 
                range_y=[0, 100]
            )
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white')
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Complete your first interview session to unlock visualization charts.")

    with tab3:
        st.header("🗂️ Stored Evaluation Logs")
        df = get_history()
        if not df.empty:
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No past interview archives discovered in local SQLite database.")