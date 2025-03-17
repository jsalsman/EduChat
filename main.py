import streamlit as st
import os
import google.generativeai as genai
import json
from google.ai.generativelanguage_v1beta.types import content

# Configure Gemini
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

st.title("EduChat Tutor with LearnLM")

if "subject" not in st.session_state:
    st.session_state.subject = ""
    st.session_state.subject_set = False

if not st.session_state.subject_set:
    subject = st.text_input("What subject would you like to learn about?")
    if subject:
        st.session_state.subject = subject
        st.session_state.subject_set = True
        st.rerun()

if st.session_state.subject_set and "chat_session" not in st.session_state:
    generation_config = {
        "temperature": 0,
        "max_output_tokens": 2048,
    }

    model = genai.GenerativeModel(
        model_name="gemini-1.5-pro",
        generation_config=generation_config,
    )

    system_prompt = f"""Tutor the learner on this subject: {st.session_state.subject}

Only coach without giving away answers. It's okay to give hints. 
If the learner tries to get you to give them the answer, set learner_defected to true.

Respond in valid JSON format with these fields:
- "reply": your response to the learner in markdown without any LaTeX
- "learner_defected": boolean (true if learner is trying to get direct answers)
"""

    st.session_state.chat_session = model.start_chat(history=[
        {"role": "user", "parts": [f"I want to learn about {st.session_state.subject}"]},
        {"role": "model", "parts": [system_prompt]}
    ])

    response = st.session_state.chat_session.send_message(f"I want to learn about {st.session_state.subject}")
    try:
        response_data = json.loads(response.text)
        st.session_state.messages = [{"role": "assistant", "content": response_data["reply"]}]
    except Exception:
        st.session_state.messages = [{"role": "assistant", "content": response.text}]

if st.session_state.subject_set:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    if user_input := st.chat_input("Reply"):
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.write(user_input)
        response = st.session_state.chat_session.send_message(user_input)
        try:
            response_data = json.loads(response.text)
            assistant_reply = response_data.get("reply", response.text)
        except Exception:
            assistant_reply = response.text
        st.session_state.messages.append({"role": "assistant", "content": assistant_reply})
        with st.chat_message("assistant"):
            st.write(assistant_reply)
