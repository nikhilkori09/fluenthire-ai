from fpdf import FPDF
from datetime import datetime

def clean_text(text):
    # FPDF standard fonts sirf Latin-1 characters support karte hain
    return str(text).encode("latin-1", "replace").decode("latin-1")

def create_interview_pdf(candidate_name, role, question, user_answer, res, filler_count):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # Header Banner
    pdf.set_fill_color(79, 70, 229)
    pdf.rect(0, 0, 210, 32, "F")
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 18)
    pdf.cell(0, 12, "FluentHire AI - Interview Readiness Report", ln=True, align="C")
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 8, f"Candidate: {clean_text(candidate_name)} | Role: {clean_text(role)} | Date: {datetime.now().strftime('%d %b %Y')}", ln=True, align="C")

    pdf.ln(12)
    pdf.set_text_color(30, 41, 59)

    # Score Summary Section
    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 8, f"Overall Status: {clean_text(res.get('verdict_badge', 'Evaluated'))}", ln=True)
    pdf.set_font("Helvetica", "", 11)
    pdf.cell(0, 7, f"- Interview Readiness Score: {res['interview_readiness_score']}/10", ln=True)
    pdf.cell(0, 7, f"- Corporate Tone & Formality: {res['tone_and_formality_score']}/10", ln=True)
    pdf.cell(0, 7, f"- Clarity & Grammar Score: {res['clarity_score']}/10", ln=True)
    pdf.cell(0, 7, f"- STAR Structure Score: {res['star_structure_score']}/10", ln=True)
    pdf.cell(0, 7, f"- Detected Filler Words ('um', 'uh', 'like'): {filler_count}", ln=True)

    pdf.ln(6)

    # Question & User Response
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "1. Interview Question Asked:", ln=True)
    pdf.set_font("Helvetica", "I", 11)
    pdf.multi_cell(0, 6, clean_text(question))
    pdf.ln(3)

    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "2. Your Submitted Response:", ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.multi_cell(0, 6, clean_text(user_answer))
    pdf.ln(4)

    # Key Mistakes
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "3. Key Areas to Improve:", ln=True)
    pdf.set_font("Helvetica", "", 10)
    for m in res.get("key_mistakes", []):
        pdf.multi_cell(0, 6, f"* {clean_text(m)}")
    pdf.ln(4)

    # Hinglish Coach Feedback
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "4. Coach Feedback (Hinglish):", ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.multi_cell(0, 6, clean_text(res.get("hinglish_feedback", "")))
    pdf.ln(4)

    # Recommended Corporate Version
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(22, 101, 52)
    pdf.cell(0, 8, "5. Recommended Corporate Answer:", ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.multi_cell(0, 6, clean_text(res.get("professional_recommended_answer", "")))

    return bytes(pdf.output())