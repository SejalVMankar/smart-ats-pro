import streamlit as st
import google.generativeai as genai
import os
import PyPDF2 as pdf
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Google Gemini API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Function to get Gemini response
def get_gemini_response(input_text):
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(input_text)
    return response.text

# Function to extract PDF text
def input_pdf_text(uploaded_file):
    reader = pdf.PdfReader(uploaded_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

# Enhanced prompt template
input_prompt = """
Act as a highly experienced ATS (Applicant Tracking System) specialist with deep knowledge of 
tech roles including software engineering, data science, and cloud computing. Analyze this 
resume against the job description and provide detailed feedback:

Resume: {text}
Job Description: {jd}

Provide response in this EXACT JSON format:
{{
  "score": "X/100",
  "missing_keywords": ["keyword1", "keyword2"],
  "existing_keywords": ["keyword3", "keyword4"],
  "skill_gaps": ["skill1", "skill2"],
  "summary": "Detailed analysis summary...",
  "suggestions": [
    "Suggestion 1...",
    "Suggestion 2..."
  ],
  "salary_estimation": {{
    "min": "X",
    "max": "Y",
    "currency": "USD",
    "notes": "Salary estimation based on skills and industry standards."
  }}
}}

Important:
1. Score should reflect overall match percentage
2. List at least 5 missing keywords from JD
3. Identify 3 key skill gaps
4. Provide 3 actionable suggestions
5. Estimate salary range based on skills and industry standards
6. Never use markdown formatting
"""

# Streamlit UI
st.set_page_config(page_title="Smart ATS Pro", layout="wide")

# Header Section
col1, col2 = st.columns([1, 3])
with col1:
    st.image("https://cdn-icons-png.flaticon.com/512/3135/3135679.png", width=100)
with col2:
    st.title("Smart ATS Pro")
    st.caption("AI-Powered Resume Optimization System")

# Main Input Section
with st.expander("📁 Upload Documents", expanded=True):
    jd = st.text_area("📝 Paste Job Description", height=150)
    resume_file = st.file_uploader("📄 Upload Resume (PDF)", type=["pdf"])

# Analysis Parameters
with st.expander("⚙️ Analysis Settings"):
    analysis_depth = st.select_slider(
        "Analysis Depth",
        options=["Basic", "Standard", "Detailed"],
        value="Standard"
    )
    industry = st.selectbox(
        "Target Industry",
        ("Tech", "Finance", "Healthcare", "Manufacturing")
    )

# Process Documents
if st.button("🚀 Analyze Documents") and resume_file and jd:
    with st.spinner("🔍 Analyzing documents..."):
        try:
            # Extract and process text
            resume_text = input_pdf_text(resume_file)
            
            # Generate analysis
            formatted_prompt = input_prompt.format(text=resume_text, jd=jd)
            response = get_gemini_response(formatted_prompt)
            
            # Parse JSON response
            analysis = json.loads(response)

            # Display Results
            st.success("✅ Analysis Complete!")
            
            # Score Card
            st.subheader("📊 Match Analysis")
            score = int(analysis["score"].split("/")[0])
            st.progress(score/100)
            
            # Columns Layout
            col1, col2 = st.columns(2)
            
            with col1:
                # Missing Keywords
                with st.expander("🔍 Missing Keywords", expanded=True):
                    st.write("These keywords from the JD are missing in your resume:")
                    for kw in analysis["missing_keywords"]:
                        st.error(f"- {kw}")
                
                # Skill Gaps
                with st.expander("📉 Skill Gaps"):
                    for gap in analysis["skill_gaps"]:
                        st.warning(f"- {gap}")
            
            with col2:
                # Existing Keywords
                with st.expander("✅ Matching Keywords"):
                    st.write("These important keywords were found in your resume:")
                    for kw in analysis["existing_keywords"]:
                        st.success(f"- {kw}")
                
                # Suggestions
                with st.expander("💡 Improvement Suggestions"):
                    for suggestion in analysis["suggestions"]:
                        st.info(f"- {suggestion}")
            
            # Salary Estimation
            st.subheader("💰 Salary Estimation")
            salary = analysis["salary_estimation"]
            st.write(f"**Range:** {salary['min']} - {salary['max']} {salary['currency']}")
            st.caption(salary["notes"])
            
            # Summary Section
            st.subheader("📝 Executive Summary")
            st.write(analysis["summary"])
            
            # Download Report
            report = f"""
            Smart ATS Pro Report\n-------------------\n
            Score: {analysis["score"]}\n
            Missing Keywords: {", ".join(analysis["missing_keywords"])}\n
            Skill Gaps: {", ".join(analysis["skill_gaps"])}\n
            Suggestions:\n- {"\n- ".join(analysis["suggestions"])}\n
            Salary Estimation: {salary['min']} - {salary['max']} {salary['currency']}
            """
            st.download_button("📥 Download Report", report, file_name="ats_report.txt")
            
        except Exception as e:
            st.error(f"Error: {str(e)}")
            st.error("Please try again or check your document formatting.")

# Sidebar with Instructions
with st.sidebar:
    st.header("📖 How to Use")
    st.markdown("""
    1. 📝 Paste job description in main area
    2. 📄 Upload PDF resume
    3. ⚙️ Adjust settings if needed
    4. 🚀 Click Analyze Documents
    5. 💡 Review results & improve resume!
    """)
    
    st.divider()
    st.header("🛠️ Features")
    st.markdown("""
    - AI-powered resume scoring
    - Keyword gap analysis
    - Skill gap identification
    - Salary estimation
    - Actionable improvement tips
    - Industry-specific insights
    """)
    
    st.divider()
    st.write("⚠️ Important Notes:")
    st.markdown("""
    - Works best with PDF resumes
    - Avoid scanned documents
    - Keep JD under 2000 words
    - Results may take 20-30 seconds
    """)

# Footer
st.divider()
st.markdown("""
<small>Powered by Google Gemini • Built with Streamlit</small>
""", unsafe_allow_html=True)