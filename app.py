import os
import time
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from pypdf import PdfReader
from evaluator import (
    evaluate_interview_response,
    generate_daily_drill,
    generate_resume_questions,
    transcribe_audio_gemini,
    text_to_speech,
    count_filler_words
)
from database import init_db, save_session, get_all_sessions
from pdf_generator import create_interview_pdf

load_dotenv(override=True)
init_db()

st.set_page_config(
    page_title="FluentHire AI | Interview & English Studio",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom SaaS CSS
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%);
        color: #f8fafc;
    }
    .hero-banner {
        background: linear-gradient(90deg, #4f46e5 0%, #7c3aed 50%, #db2777 100%);
        padding: 1.8rem;
        border-radius: 16px;
        margin-bottom: 1.5rem;
        box-shadow: 0 10px 25px -5px rgba(124, 58, 237, 0.4);
    }
    .hero-title {
        font-size: 2.1rem;
        font-weight: 800;
        color: #ffffff;
        margin: 0;
    }
    .hero-sub {
        font-size: 0.95rem;
        color: #e0e7ff;
        margin-top: 0.3rem;
    }
    .kpi-card {
        background: rgba(30, 41, 59, 0.75);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 14px;
        padding: 1.1rem;
        text-align: center;
    }
    .kpi-value {
        font-size: 1.85rem;
        font-weight: 700;
        color: #38bdf8;
    }
    .kpi-label {
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        color: #94a3b8;
        margin-top: 4px;
    }
    .question-card {
        background: rgba(15, 23, 42, 0.85);
        border-left: 5px solid #8b5cf6;
        padding: 1.3rem;
        border-radius: 10px;
        margin: 1rem 0;
        font-size: 1.15rem;
    }
    .stButton>button {
        background: linear-gradient(90deg, #6366f1, #8b5cf6);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.6rem 1.4rem;
        font-weight: 600;
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("## 🎙️ FluentHire AI")
    st.caption("Corporate English & Interview Readiness Studio")
    
    # Direct API Key Input (Works even if .env fails)
    default_env_key = os.getenv("GEMINI_API_KEY", "")
    if default_env_key == "your_api_key_here":
        default_env_key = ""
    api_key_input = st.text_input(
        "🔑 Gemini API Key",
        value=default_env_key,
        type="password",
        placeholder="Paste AIzaSy... key here"
    )
    st.divider()

    candidate_name = st.text_input("Candidate Name", value="Riya")
    target_role = st.selectbox(
        "🎯 Target Job Track",
        [
            "AI / ML & Python Fresher",
            "Data Analyst",
            "Software Developer (SDE-1)",
            "HR & Operations",
            "Campus Placement General"
        ]
    )
    proficiency_level = st.select_slider(
        "📊 Current English Level",
        options=["Beginner (A1-A2)", "Intermediate (B1-B2)", "Advanced (C1)"]
    )

    st.divider()
    st.markdown("### 📄 Resume-Based Questions")
    uploaded_resume = st.file_uploader("Upload Resume (PDF)", type=["pdf"])
    if uploaded_resume is not None:
        if st.button("✨ Generate Resume Questions"):
            try:
                with st.spinner("Reading resume & crafting questions..."):
                    reader = PdfReader(uploaded_resume)
                    resume_text = "\n".join([page.extract_text() or "" for page in reader.pages])
                    st.session_state["resume_questions"] = generate_resume_questions(resume_text, target_role, api_key_input)
                    st.success("Personalized questions ready!")
            except Exception as e:
                st.error(f"Error: {e}")

    st.divider()
    history_df = get_all_sessions()
    st.metric("🔥 Mock Tests Completed", len(history_df))
    if not history_df.empty:
        st.metric("⭐ Avg Readiness Score", f"{round(history_df['readiness_score'].mean(), 1)} / 10")

# --- HERO HEADER ---
st.markdown(f"""
<div class="hero-banner">
    <div class="hero-title">Welcome back, {candidate_name} 👋</div>
    <div class="hero-sub">Track: <b>{target_role}</b> • Level: <b>{proficiency_level}</b> • Voice AI, Resume RAG & PDF Reports</div>
</div>
""", unsafe_allow_html=True)

# --- 4 NAVIGATION TABS ---
tab1, tab2, tab3, tab4 = st.tabs([
    "🎤 Mock Interview Studio",
    "⚡ Daily English Drills",
    "📘 Corporate Cheat-Sheet",
    "📈 Readiness Analytics & History"
])

# ==========================================
# TAB 1: MOCK INTERVIEW STUDIO
# ==========================================
with tab1:
    default_questions = {
        "AI / ML & Python Fresher": [
            "Walk me through an AI or Python project you built from scratch.",
            "How do you explain a complex technical model to a non-technical manager?",
            "Describe a bug or bottleneck you faced during development and how you fixed it."
        ],
        "Data Analyst": [
            "How do you clean a messy dataset before building a dashboard?",
            "Tell me about a time your data analysis uncovered an unexpected insight.",
            "Explain the difference between correlation and causation in business metrics."
        ],
        "Software Developer (SDE-1)": [
            "Why should we hire you over other computer science freshers?",
            "Describe a situation where you had to learn a new tool or framework quickly.",
            "How do you handle tight deadlines and code reviews?"
        ],
        "HR & Operations": [
            "Tell me about yourself and why you are interested in this role.",
            "Describe a conflict in a team project and how you resolved it.",
            "Where do you see yourself professionally in the next 3 years?"
        ],
        "Campus Placement General": [
            "Introduce yourself in 60 seconds focusing on your strengths and skills.",
            "What is your biggest achievement during college?",
            "Tell me about a failure or setback and what you learned from it."
        ]
    }

    available_questions = st.session_state.get("resume_questions", []) + default_questions[target_role]

    col_q1, col_q2, col_q3 = st.columns([3, 1, 1])
    with col_q1:
        selected_question = st.selectbox("Select Interview Prompt (Resume Questions appear on top):", available_questions)
    with col_q2:
        if st.button("🔊 Listen Question"):
            audio_path = text_to_speech(selected_question, "question_audio.mp3")
            st.audio(audio_path, autoplay=True)
    with col_q3:
        if st.button("⏱️ 60s Pressure Timer"):
            timer_placeholder = st.empty()
            for sec in range(60, -1, -1):
                timer_placeholder.warning(f"⏳ Time Left: **{sec}s** — Speak concisely!")
                time.sleep(1)
            timer_placeholder.error("🛑 Time's up! Wrap up your closing sentence.")

    st.markdown(f'<div class="question-card">💬 <b>Interviewer:</b> "{selected_question}"</div>', unsafe_allow_html=True)

    input_mode = st.radio("Choose Answer Mode:", ["🎙️ Speak via Microphone", "⌨️ Type Answer"], horizontal=True)

    if input_mode == "🎙️ Speak via Microphone":
        audio_data = st.audio_input("Record your spoken interview answer:")
        if audio_data is not None:
            try:
                with st.spinner("Transcribing your voice & analyzing fluency..."):
                    transcribed_text = transcribe_audio_gemini(audio_data.getvalue(), audio_data.type, api_key_input)
                    st.session_state["spoken_transcript"] = transcribed_text
            except Exception as e:
                st.error(f"Transcription Error: {e}")
        user_response = st.text_area(
            "Transcribed Speech (You can review before auditing):",
            value=st.session_state.get("spoken_transcript", ""),
            height=130
        )
    else:
        user_response = st.text_area(
            "Type your response naturally as you would speak in an interview:",
            height=140,
            placeholder="e.g. Good morning, my name is Riya..."
        )

    word_count = len(user_response.split()) if user_response.strip() else 0
    filler_count = count_filler_words(user_response) if user_response.strip() else 0
    st.caption(f"📊 Word Count: **{word_count}** words (Ideal: 60–140) | 🗣️ Filler Words Detected ('um', 'uh', 'like'): **{filler_count}**")

    if st.button("🚀 Run Full Interview Readiness Audit"):
        if not user_response.strip():
            st.warning("Please speak or type your answer first.")
        else:
            with st.spinner("Auditing corporate tone, STAR structure, grammar & generating PDF report..."):
                try:
                    res = evaluate_interview_response(target_role, selected_question, user_response, api_key_input)
                    save_session(
                        target_role,
                        selected_question,
                        res["interview_readiness_score"],
                        res["tone_and_formality_score"],
                        res["clarity_score"],
                        res["star_structure_score"]
                    )
                    st.session_state["last_audit"] = {
                        "res": res,
                        "question": selected_question,
                        "answer": user_response,
                        "fillers": filler_count
                    }
                except Exception as e:
                    st.error(f"Evaluation Error: {e}")

    if "last_audit" in st.session_state:
        audit = st.session_state["last_audit"]
        res = audit["res"]

        st.success(f"Audit Complete — Status: **{res['verdict_badge']}**")

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(f'<div class="kpi-card"><div class="kpi-value">{res["interview_readiness_score"]}/10</div><div class="kpi-label">Readiness</div></div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div class="kpi-card"><div class="kpi-value">{res["tone_and_formality_score"]}/10</div><div class="kpi-label">Corporate Tone</div></div>', unsafe_allow_html=True)
        with c3:
            st.markdown(f'<div class="kpi-card"><div class="kpi-value">{res["clarity_score"]}/10</div><div class="kpi-label">Clarity</div></div>', unsafe_allow_html=True)
        with c4:
            st.markdown(f'<div class="kpi-card"><div class="kpi-value">{res["star_structure_score"]}/10</div><div class="kpi-label">STAR Structure</div></div>', unsafe_allow_html=True)

        st.write("")
        col_left, col_right = st.columns(2)

        with col_left:
            st.subheader("💡 Coach Feedback (Hinglish)")
            st.info(res["hinglish_feedback"])

            st.subheader("⚠️ Areas to Fix")
            for m in res["key_mistakes"]:
                st.markdown(f"- {m}")