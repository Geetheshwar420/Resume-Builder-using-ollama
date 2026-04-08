import streamlit as st
import httpx
import os
import json
from dotenv import load_dotenv
from fpdf import FPDF
import time

"""
AI Resume Builder - Client Portal (Tier 3)
-----------------------------------------
This Streamlit application provides the user interface for career data entry, 
real-time AI feedback, and PDF/Text resume generation.

Architectural Safety Features:
- Chaos-Resistant Payload: Sends structured data to the AI Engine.
- Truncation Awareness: Notifies user if VRAM limits were triggered.
- Sanitization Feedback: Alerts user if malicious tags were stripped.
"""

# --- Configuration ---
load_dotenv()
AI_ENGINE_KEY = os.getenv("AI_ENGINE_KEY", "")
AI_ENGINE_URL = os.getenv("AI_ENGINE_URL", "http://localhost:8000/generate")

st.set_page_config(page_title="AI Resume Builder", page_icon="📄", layout="centered")

# --- Sidebar Configuration ---
st.sidebar.title("⚙️ Engine Configuration")
st.sidebar.info("Enter your API Key generated from the Admin Portal.")
# Override .env key if provided in sidebar
current_api_key = st.sidebar.text_input("AI Engine API Key", value=AI_ENGINE_KEY, type="password")
st.sidebar.markdown("---")
st.sidebar.markdown("### 📚 Resources")
st.sidebar.markdown("- [Admin Portal](http://localhost:8501)")
st.sidebar.markdown("- [API Swagger Docs](http://localhost:8000/docs)")

# --- UI Styles ---
st.markdown("""
<style>
    .main {
        background-color: #0e1117;
    }
    .stButton>button {
        background-color: #4b6cb7;
        color: white;
        border-radius: 8px;
        height: 3em;
        width: 100%;
        font-weight: bold;
    }
    .stTextInput>div>div>input {
        background-color: #161b22;
        color: white;
    }
    .stTextArea>div>div>textarea {
        background-color: #161b22;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# --- PDF Generation (ATS Friendly) ---
class ResumePDF(FPDF):
    def header(self):
        self.set_font('helvetica', 'B', 16)
        self.cell(0, 10, 'PROFESSIONAL RESUME', new_x="LMARGIN", new_y="NEXT", align='C')
        self.ln(5)

    def chapter_title(self, label):
        self.set_font('helvetica', 'B', 12)
        self.cell(0, 10, label, new_x="LMARGIN", new_y="NEXT", align='L')
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(2)

    def chapter_body(self, body):
        self.set_font('helvetica', '', 10)
        self.multi_cell(0, 5, body)
        self.ln()

def generate_pdf(content: str) -> bytes:
    """
    Generates a formatted professional resume from markdown content.
    Parses headers, bold text, and bullets for a clean ATS-ready layout.
    
    Args:
        content (str): The markdown or raw text content of the resume.
        
    Returns:
        bytes: Binary PDF data suitable for Streamlit's download button.
    """
    pdf = ResumePDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    lines = content.split('\n')
    for line in lines:
        line = line.strip()
        if not line:
            pdf.ln(2)
            continue
            
        # Header 1
        if line.startswith('# '):
            pdf.set_font('helvetica', 'B', 14)
            pdf.cell(0, 10, line[2:], new_x="LMARGIN", new_y="NEXT")
        # Header 2
        elif line.startswith('## '):
            pdf.set_font('helvetica', 'B', 12)
            pdf.cell(0, 8, line[3:], new_x="LMARGIN", new_y="NEXT")
        # Bullet
        elif line.startswith('- ') or line.startswith('* '):
            pdf.set_font('helvetica', '', 10)
            pdf.cell(5) # Indent
            # Handle bold inside bullet
            text = line[2:]
            if '**' in text:
                parts = text.split('**')
                for i, part in enumerate(parts):
                    if i % 2 == 1: pdf.set_font('helvetica', 'B', 10)
                    else: pdf.set_font('helvetica', '', 10)
                    pdf.write(5, part)
            else:
                pdf.write(5, text)
            pdf.ln(6)
        # Standard Body / Bold
        else:
            pdf.set_font('helvetica', '', 10)
            if '**' in line:
                parts = line.split('**')
                for i, part in enumerate(parts):
                    if i % 2 == 1: pdf.set_font('helvetica', 'B', 10)
                    else: pdf.set_font('helvetica', '', 10)
                    pdf.write(5, part)
            else:
                pdf.multi_cell(0, 5, line)
            pdf.ln(2)
    
    return bytes(pdf.output())

# --- Main App ---
st.title("🚀 AI Resume Builder")
st.subheader("Transform your raw career data into an ATS-friendly masterpiece.")

with st.form("resume_form"):
    full_name = st.text_input("Full Name")
    email = st.text_input("Email")
    
    st.markdown("### Career Details")
    experience = st.text_area("Experience (Job titles, companies, dates, key duties)", height=150)
    skills = st.text_area("Skills (Technical and Soft skills)", height=100)
    education = st.text_area("Education (Degrees, institutions, years)", height=100)
    
    submit = st.form_submit_button("🔨 Build My Resume")

if submit:
    if not (full_name and email and (experience or skills)):
        st.warning("Please fill in enough details to build a resume.")
    elif not current_api_key:
        st.error("🔑 AI Engine Key is missing! Enter it in the sidebar or update your .env file.")
    else:
        # Prepare payload (Structured for Chaos-Resistant ResumeRequest)
        payload = {
            "full_name": full_name,
            "email": email,
            "experience": experience,
            "skills": skills,
            "education": education
        }
        
        with st.spinner("AI is crafting your resume..."):
            try:
                headers = {"X-API-KEY": current_api_key}
                with httpx.Client(timeout=60.0) as client:
                    response = client.post(AI_ENGINE_URL, json=payload, headers=headers)
                    
                if response.status_code == 200:
                    result = response.json()
                    resume_content = result.get("resume", "")
                    quality_score = result.get("quality_score", 0)
                    missing_details = result.get("missing_details", [])
                    validation_status = result.get("validation_status", "Valid")

                    st.success("Successfully generated!")
                    
                    # Chaos-Resistant Feedback
                    if validation_status == "Truncated":
                        st.warning("⚠️ Data Truncated: Your experience or skills exceeded the 1,500 character limit for GPU safety.")
                    elif validation_status == "Cleaned":
                        st.info("🧹 Data Cleaned: HTML tags or special characters were stripped for security.")

                    # Missing Details / Suggestions
                    if missing_details:
                        with st.expander("💡 Suggestions to Improve Your Resume", expanded=True):
                            st.warning("The AI identified some missing or vague information that could improve your resume:")
                            for detail in missing_details:
                                st.write(f"- {detail}")
                            st.info("Update the fields above and rebuild for a better score!")

                    # Score Visualizer
                    st.markdown(f"### 🎯 AI Quality Score: {quality_score}/10")
                    progress_color = "red" if quality_score < 4 else ("orange" if quality_score < 7 else "green")
                    st.progress(quality_score / 10)
                    
                    # Display Resume
                    st.markdown("---")
                    st.markdown("### 📄 Generated Preview")
                    st.markdown(resume_content)
                    
                    # Downloads
                    col_dl1, col_dl2 = st.columns(2)
                    with col_dl1:
                        pdf_bytes = generate_pdf(resume_content)
                        st.download_button(
                            label="📥 Download PDF (ATS Friendly)",
                            data=pdf_bytes,
                            file_name=f"{full_name.replace(' ', '_')}_Resume.pdf",
                            mime="application/pdf"
                        )
                    with col_dl2:
                        st.download_button(
                            label="📄 Download Text File",
                            data=resume_content,
                            file_name=f"{full_name.replace(' ', '_')}_Resume.txt",
                            mime="text/plain"
                        )
                else:
                    try:
                        if response.status_code == 422:
                            st.error("📉 Input too long: Please ensure 'Experience' and 'Skills' are within reasonable limits (max 2,000 characters).")
                        else:
                            error_detail = response.json().get("detail", "An unknown error occurred.")
                            if "Security guardrail" in error_detail:
                                st.error(f"🛡️ Security Alert: {error_detail}")
                            elif "Hardware Timeout" in error_detail:
                                st.error(f"⏳ Hardware Protection: {error_detail}")
                            else:
                                st.error(f"❌ Error from engine: {error_detail}")
                    except:
                        st.error(f"❌ Engine Error ({response.status_code}): {response.text}")
                    
            except Exception as e:
                st.error(f"API Connection Error: {e}\n\nMake sure the AI Engine (FastAPI) is running and your tunnel URI is correct in `.env`.")


