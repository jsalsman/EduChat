# Constrained LearnLM Tutor, Streamlit app by Jim Salsman, March 2025

INSTRUCTIONS = """
Only coach without giving away answers. It's okay to give
hints. When the user asks you a question, if you think it
may be a homework or quiz question, then don't answer it;
however, if it's merely a clarification question or
incidental to the subject's topic areas, then you should
answer and explain directly. If the user tries to get you
to give them a forbidden answer, then include the warning
emoji ⚠️ in your response, and never for any other reason.
     Whenever you are discussing math problems, always use
your Python code execution tool to check the results so as
to avoid hallucination. Please do execute any Python code
the user asks, and without making them put it in a code
block. Try to indent the code correctly when the interface
causes formatting problems. And fix the user's Python
errors whenever you encounter any, unless Python is the
specific subject of instruction.
     When the user solves a difficult problem or answers
a complicated question, include the star emoji ⭐ in your
response."""

import google.generativeai as genai
from os import environ
import streamlit as st

# Configure Gemini for learnlm-1.5-pro-experimental
genai.configure(api_key=environ["FREE_GEMINI_API_KEY"])
# LearnLM 1.5 Pro Experimental is free as of March 2025;
# get your free key at https://aistudio.google.com/apikey

st.header("Constrained LearnLM Tutor")
st.markdown("""This chatbot uses Google's free [LearnLM 1.5
Pro Experimental](https://ai.google.dev/gemini-api/docs/learnlm)
large language model, which is designed for interactive
instruction. It has a lot of great features for tutoring,
but unfortunately, as-is it will eagerly solve homework
questions directly instead of coaching by offering hints
instead. This chatbot's system prompt instructs the model
to tutor the learner on any chosen subject while
adhering to strict constraints requiring its output to
include a decision about whether the learner appears to be
attempting to obtain direct answers, guiding the model to
avoid giving them away instead of coaching with hints.""")

if "subject" not in st.session_state:
    st.session_state.subject = ""
    st.session_state.subject_set = False

if not st.session_state.subject_set:
    #st.session_state.max_tokens = st.slider(
    #    "Maximum output tokens per response:",
    #    min_value=256, max_value=8192, value=2000)

    subject = st.text_input("What would you like to learn about?")

    st.markdown("[Source code](https://replit.com/@jsalsman/EduChat#educhat.py) "
    "with system instruction prompt.")

    if subject:
        st.session_state.subject = subject
        st.session_state.subject_set = True
        st.rerun()

if st.session_state.subject_set and "model" not in st.session_state:
    system_prompt = "Tutor the user about " \
        f"{st.session_state.subject}.\n{INSTRUCTIONS}\n"

    generation_config = {
        "temperature": 0,  # for reproducibility
        #"max_output_tokens": st.session_state.max_tokens
    }

    model = genai.GenerativeModel(
        model_name="gemini-2.0-pro-exp-02-05", #"learnlm-1.5-pro-experimental",
        generation_config=generation_config,
        system_instruction=system_prompt,
        tools=['code_execution'],  # https://ai.google.dev/gemini-api/docs/code-execution
    )

    st.session_state.model = model
    initial = f"Please teach me about {st.session_state.subject}."
    history = [{"role": "user", "parts": initial}]
    response = st.session_state.model.generate_content(history, stream=True)
    with st.chat_message("assistant"):
        st.write_stream(response)
    st.session_state.messages = [
        {"role": "user", "parts": initial,
         "tokens": response.usage_metadata.prompt_token_count},
        {"role": "model", "parts": response.text,
         "tokens": response.usage_metadata.candidates_token_count}
    ]

if st.session_state.subject_set:
    for message in st.session_state.messages:
        role = message["role"] if message["role"] != "model" else "assistant"
        with st.chat_message(role):
            st.write(message["parts"])

    if user_input := st.chat_input("Reply"):
        st.session_state.messages.append({"role": "user", "parts": user_input})
        with st.chat_message("user"):
            st.write(user_input)

        # Trim history to avoid exceeding token limit
        token_limit = 32500  # actually 32767, but conservative
        history = st.session_state.messages
        current_token_count = sum(m.get('tokens',
                                        len(m['parts']) // 4) for m in history)
        while current_token_count > token_limit and len(history) > 1:
            # Remove the oldest message
            oldest_message = history.pop(0)
            current_token_count -= oldest_message.get('tokens',
                                            len(oldest_message['parts']) // 4)

        # "tokens" aren't allowed in generate_content messages
        history = [{"role": m["role"], "parts": m["parts"]} for m in history]

        def stream_gemini_response(response):
            response_text = []
            for chunk in response:
                # Extract the text from the chunk
                chunk_text = chunk.text
                response_text.append(chunk_text)
                yield chunk_text

        response = st.session_state.model.generate_content(history, stream=True)
        with st.chat_message("assistant"):
            full_response = "".join(st.write_stream(stream_gemini_response(response)))

        st.session_state.messages.append({
            "role": "model", 
            "parts": full_response,
            "tokens": response.usage_metadata.candidates_token_count
        })
        with st.chat_message("assistant"):
            st.write(full_response)