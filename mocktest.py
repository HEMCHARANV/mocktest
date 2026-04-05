import streamlit as st
import fitz  # PyMuPDF
import re
import time
from datetime import timedelta

# -----------------------------
# Function to parse questions
# -----------------------------
def parse_question_paper(pdf_file):
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    full_text = ""

    for page in doc:
        full_text += page.get_text()

    questions = []

    # Match questions (1. or 1))
    q_pattern = r"(\d+[\.\)])\s*(.*?)(?=\n\d+[\.\)]|\Z)"
    matches = re.findall(q_pattern, full_text, re.DOTALL)

    for q_num, content in matches:
        # Extract options A-D
        opt_pattern = r"([A-D][\.\)])\s*(.*?)(?=[A-D][\.\)]|\Z)"
        options = re.findall(opt_pattern, content, re.DOTALL)

        # Extract question text (before options)
        q_text_split = re.split(r"[A-D][\.\)]", content)
        q_text = q_text_split[0].strip()

        questions.append({
            "number": q_num.strip(),
            "text": q_text,
            "options": [f"{o[0]} {o[1].strip()}" for o in options]
        })

    return questions


# -----------------------------
# UI
# -----------------------------
st.set_page_config(page_title="Mock Test", layout="wide")
st.title("🚀 Automated Mock Test Environment")

uploaded_file = st.file_uploader("Upload Question Paper (PDF)", type="pdf")


# -----------------------------
# Initialize session state
# -----------------------------
if uploaded_file:
    if "questions" not in st.session_state:
        st.session_state.questions = parse_question_paper(uploaded_file)
        st.session_state.start_time = time.time()
        st.session_state.duration = 3 * 3600  # 3 hours
        st.session_state.submitted = False


# -----------------------------
# Main Logic
# -----------------------------
if "questions" in st.session_state:

    # Timer
    elapsed = time.time() - st.session_state.start_time
    remaining = max(0, st.session_state.duration - elapsed)

    st.sidebar.header("⏳ Timer")
    st.sidebar.write(str(timedelta(seconds=int(remaining))))

    answers = {}

    # -----------------------------
    # Show Questions
    # -----------------------------
    if not st.session_state.submitted and remaining > 0:

        for i, q in enumerate(st.session_state.questions):
            st.write(f"### Question {q['number']}")
            st.write(q['text'])

            answer = st.radio(
                "Select an option:",
                q['options'],
                key=f"q_{i}"   # ✅ UNIQUE KEY FIX
            )

            answers[q['number']] = answer
            st.divider()

        # Submit Button
        if st.button("✅ Submit Test"):
            st.session_state.submitted = True
            st.session_state.answers = answers
            st.success("Test Submitted Successfully!")

    # -----------------------------
    # Auto Submit when time ends
    # -----------------------------
    elif remaining <= 0 and not st.session_state.submitted:
        st.session_state.submitted = True
        st.warning("⏰ Time's Up! Test auto-submitted.")

    # -----------------------------
    # After Submission
    # -----------------------------
    if st.session_state.submitted:
        st.header("📄 Your Responses")

        for i, q in enumerate(st.session_state.questions):
            user_ans = st.session_state.get("answers", {}).get(q['number'], "Not Answered")

            st.write(f"**Question {q['number']}**")
            st.write(q['text'])
            st.write(f"👉 Your Answer: {user_ans}")
            st.divider()