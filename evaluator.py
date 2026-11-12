import os
import re
import json
import asyncio
import edge_tts
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv(override=True)

def get_client(api_key: str = None):
    key = (api_key or os.getenv("GEMINI_API_KEY") or "").strip().strip('"').strip("'")
    if not key or key == "your_api_key_here":
        raise ValueError("Valid Gemini API Key missing! Sidebar me apni AIzaSy... wali key paste karein.")
    return genai.Client(api_key=key)

def count_filler_words(text: str) -> int:
    fillers = r"\b(um+|uh+|ah+|er+|like|you know|actually|basically|literally)\b"
    matches = re.findall(fillers, text.lower())
    return len(matches)

def transcribe_audio_gemini(audio_bytes: bytes, mime_type: str = "audio/wav", api_key: str = None) -> str:
    client = get_client(api_key)
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[
            types.Part.from_bytes(data=audio_bytes, mime_type=mime_type),
            "Transcribe this spoken interview response verbatim. Include filler words like 'um', 'uh', 'like' accurately if spoken. Return ONLY the transcript text."
        ]
    )
    return response.text.strip()

async def _generate_tts_async(text: str, output_file: str):
    communicate = edge_tts.Communicate(text, "en-IN-NeerjaNeural")
    await communicate.save(output_file)

def text_to_speech(text: str, filename: str = "coach_voice.mp3") -> str:
    asyncio.run(_generate_tts_async(text, filename))
    return filename

def generate_resume_questions(resume_text: str, role: str, api_key: str = None) -> list:
    client = get_client(api_key)
    prompt = f"""
    You are a Senior Technical & HR Interviewer hiring for the role: {role}.
    Read the candidate's resume text below and generate 4 sharp, personalized interview questions based specifically on their projects, skills, and background.
    
    Resume Text:
    {resume_text[:4000]}
    
    Return ONLY a JSON list of 4 strings.
    """
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(response_mime_type="application/json")
    )
    return json.loads(response.text)

def evaluate_interview_response(role: str, question: str, answer: str, api_key: str = None):
    client = get_client(api_key)
    prompt = f"""
    You are an elite Executive Interview & Corporate English Coach.
    Target Role: {role}
    Interview Question: {question}
    Candidate's Answer: {answer}

    Evaluate strictly for corporate interview readiness.
    Return ONLY a valid JSON object matching this exact schema:
    {{
        "interview_readiness_score": 8,
        "tone_and_formality_score": 7,
        "clarity_score": 8,
        "star_structure_score": 6,
        "verdict_badge": "Interview Ready / Needs Polish / Beginner Level",
        "key_mistakes": ["Point 1", "Point 2"],
        "vocabulary_upgrades": [
            {{"casual": "old phrase", "corporate": "upgraded corporate phrase"}}
        ],
        "hinglish_feedback": "Constructive, encouraging feedback in Hinglish",
        "professional_recommended_answer": "Polished, STAR-aligned corporate version of their answer"
    }}
    """
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(response_mime_type="application/json")
    )
    return json.loads(response.text)

def generate_daily_drill(level: str, api_key: str = None):
    client = get_client(api_key)
    prompt = f"""
    Create 3 quick English corporate sentence-correction questions for a {level} learner preparing for job interviews in India (fix common literal translations, tense errors, or casual slang).
    Return ONLY a valid JSON list of objects:
    [
        {{
            "incorrect_sentence": "Myself Riya and I passed out in 2025.",
            "options": [
                "My name is Riya, and I graduated in 2025.",
                "Myself Riya, I pass out in 2025.",
                "I am Riya and I passed away in 2025."
            ],
            "correct_option": "My name is Riya, and I graduated in 2025.",
            "explanation": "'Myself' is a reflexive pronoun and cannot start an introduction; 'passed out' means fainting, whereas 'graduated' is used for completing studies."
        }}
    ]
    """
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(response_mime_type="application/json")
    )
    return json.loads(response.text)