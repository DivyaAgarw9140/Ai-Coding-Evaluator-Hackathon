import streamlit as st
from groq import Groq
import re
import pandas as pd

# 1. Configuration & API Setup


# Secure way to handle keys on the cloud
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
client = Groq(api_key=GROQ_API_KEY)

st.set_page_config(page_title="Elite AI Code Evaluator", page_icon="🤖", layout="wide")

# 2. Custom Styling
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { background-color: #ffffff; padding: 20px; border-radius: 12px; border: 1px solid #eee; }
    .report-card { background-color: white; padding: 30px; border-radius: 15px; border: 1px solid #ddd; line-height: 1.6; }
    h1 { color: #1E1E1E; }
    </style>
    """, unsafe_allow_html=True)

# 3. Sidebar Enhancements
with st.sidebar:
    st.title("⚙️ Engine Settings")
    persona = st.selectbox("Evaluator Persona", 
                          ["Google Senior Engineer", "Startup CTO", "Clean Code Architect"],
                          help="Changes the tone and focus of the evaluation.")
    
    st.info(f"Model: Llama-3.3-70B\n\nPersona: {persona}")
    st.markdown("---")
    st.write("### 🏆 Scoring Rubric")
    st.caption("Aligned with UnsaidTalks official assessment dimensions.")

# 4. Main UI
st.title("🤖 AI Coding Assignment Evaluator")
st.write(f"Currently acting as: **{persona}**")

col1, col2 = st.columns([1, 1.2])

with col1:
    st.subheader("📥 Submission Portal")
    github_url = st.text_input("GitHub File URL (Optional)")
    uploaded_file = st.file_uploader("Upload Code Source", type=['py', 'cpp', 'java', 'js', 'c'])
    pasted_code = st.text_area("Or Paste Code Snippet:", height=300)

    if uploaded_file:
        code_input = uploaded_file.read().decode("utf-8")
        st.success("✅ File Loaded")
    else:
        code_input = pasted_code

    evaluate_btn = st.button("🚀 Run Deep-Dive Analysis")

# 5. Extraction Logic
def extract_score(text, label):
    match = re.search(fr"{label}.*?(\d+)", text, re.IGNORECASE)
    return int(match.group(1)) if match else 0

# 6. Optimized AI Prompt
def get_ai_evaluation(code, url, persona_type):
    prompt = f"""
    Act as a {persona_type}. Evaluate this coding assignment strictly.
    Provide scores out of 100 for these exact labels:
    1. Overall Score: 
    2. Correctness Score: 
    3. Efficiency Score: 
    4. Readability Score: 
    5. Modularity Score: 

    Then provide:
    - Detailed Logic Review (Big O Analysis)
    - Plagiarism & Similarity Detection (Check for boilerplate/tutorial patterns)
    - Edge Case Resilience
    - Recruiter Signal (Strong Hire / Hire / No Hire)
    - Optimized Solution (Rewrite the code for maximum performance)

    Context: {url}
    Code:
    {code}
    """
    
    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
    )
    return completion.choices[0].message.content

# 7. Execution & Results
if evaluate_btn:
    if not code_input:
        st.error("Please provide code or a file first!")
    else:
        with st.spinner(f"🕵️ {persona} is reviewing your code..."):
            try:
                result = get_ai_evaluation(code_input, github_url, persona)
                
                # Parse scores
                s1, s2, s3, s4, s5 = [extract_score(result, label) for label in 
                                     ["Overall", "Correctness", "Efficiency", "Readability", "Modularity"]]

                with col2:
                    st.subheader("📊 Performance Dashboard")
                    m1, m2, m3, m4 = st.columns(4)
                    m1.metric("Overall", f"{s1}/100")
                    m2.metric("Correctness", f"{s2}/100")
                    m3.metric("Efficiency", f"{s3}/100")
                    m4.metric("Readability", f"{s4}/100")

                    # Skill Mapping Chart
                    st.write("### 📈 Skill Mapping")
                    chart_data = pd.DataFrame({
                        'Metric': ['Correctness', 'Efficiency', 'Readability', 'Modularity'],
                        'Score': [s2, s3, s4, s5]
                    })
                    st.bar_chart(chart_data.set_index('Metric'))

                    st.markdown("---")
                    st.subheader("📝 Detailed Expert Report")
                    st.markdown(f'<div class="report-card">{result}</div>', unsafe_allow_html=True)
                    
                    st.download_button("📥 Download PDF-Ready Report", result, "evaluation_report.txt")
                    
            except Exception as e:
                st.error(f"System Error: {str(e)}")