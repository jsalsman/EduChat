# Constrained LearnLM Tutor, Streamlit app by Jim Salsman, March 2025

# System prompt
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
specific subject of instruction. You may use LaTeX
expressions, by wrapping them in "$" or "$$" (the "$$"
expressions must be on their own lines.)
     When the user solves a difficult problem or answers
a complicated question, include the star emoji ⭐ in your
response."""

import google.generativeai as genai  # pip install google-generativeai
from json import loads
from os import environ
import streamlit as st
from time import sleep  # for rate limiting retries

# Configure Gemini for learnlm-1.5-pro-experimental
genai.configure(api_key=environ["FREE_GEMINI_API_KEY"])
# LearnLM 1.5 Pro Experimental is free as of March 2025;
# get your free key at https://aistudio.google.com/apikey

st.header("Constrained LearnLM Tutor")
st.markdown("""This chatbot uses Google's free [LearnLM 1.5
Pro Experimental](https://ai.google.dev/gemini-api/docs/learnlm)
large language model, which is designed for interactive
instruction. It has a lot of great features for tutoring,
but unfortunately as-is it will eagerly solve homework
questions directly instead of coaching by offering hints
instead. This chatbot's system prompt instructs the model
to tutor the learner on any chosen subject while
adhering to strict constraints requiring its output to
include a decision about whether the learner appears to be
attempting to obtain direct answers, guiding the model to
avoid giving them away instead of coaching with hints. The
[source code](https://replit.com/@jsalsman/EduChat#educhat.py)
includes the system instruction prompt and can easily be
"re-mixed" to experiment with changes.""")

if "subject" not in st.session_state:
    st.session_state.subject = ""
    st.session_state.subject_set = False
    st.session_state.new = True
    st.session_state.messages = []
    st.session_state.model_name = None
    st.session_state.model_set = False

if not st.session_state.model_set:
    st.session_state.model_name = st.segmented_control("Use model:",
        ["learnlm-1.5-pro-experimental", "gemini-2.0-flash-lite",
         "gemini-2.0-pro-exp-02-05"], default="learnlm-1.5-pro-experimental",
        format_func=lambda model: ("LearnLM 1.5 Pro Experimental" 
                                   if model == "learnlm-1.5-pro-experimental" else
            "Gemini 2.0 Flash Lite" if model == "gemini-2.0-flash-lite" else
            "Gemini 2.0 Pro Experimental 02-05"))
else:
    st.markdown(f"Using model: ```{st.session_state.model_name}```")

if not st.session_state.subject_set:
    #st.session_state.max_tokens = st.slider(
    #    "Maximum output tokens per response:",
    #    min_value=256, max_value=8192, value=2000)

    subject = st.text_input("What would you like to learn about?")

    st.markdown("**Privacy policy:** absolutely nothing is tracked, "
                "as should be clear from the source code.")

    if subject:
        st.session_state.subject = subject
        st.session_state.subject_set = True
        st.rerun()

if st.session_state.subject_set and not st.session_state.model_set:
    system_prompt = "Tutor the user about " \
        f"{st.session_state.subject}.\n{INSTRUCTIONS}\n"

    generation_config = {
        "temperature": 0,  # for reproducibility
        #"max_output_tokens": st.session_state.max_tokens
    }

    model = genai.GenerativeModel(
        model_name=st.session_state.model_name,
        generation_config=generation_config,
        system_instruction=system_prompt,
        tools=['code_execution'],  # https://ai.google.dev/gemini-api/docs/code-execution
    )

    st.session_state.model = model
    st.session_state.model_set = True

    st.session_state.initial = f"Please teach me about {st.session_state.subject}."
    st.rerun()

if st.session_state.model_set:
    for message in st.session_state.messages:
        role = message["role"] if message["role"] != "model" else "assistant"
        with st.chat_message(role):
            st.write(message["parts"])

    if (json_input := st.chat_input("Reply", accept_file="multiple")
                ) or st.session_state.new:
        if st.session_state.new:
            user_input = st.session_state.initial
            st.session_state.new = False
        else:
            user_input = json_input.text
            files_input = json_input.files
            if files_input:  # upload files and add them to the messages
                for f in files_input:
                    file = genai.upload_file(f, display_name=f.name, mime_type=f.type, resumable=False)
                    # Count tokens using the API
                    token_count = st.session_state.model.count_tokens(file).total_tokens
                    st.write(f"Uploaded file '{file.display_name}' type {file.mime_type} with {token_count} tokens as: {file.uri}")
                    st.session_state.messages.append({"role": "user", "parts": file, "tokens": token_count})

        # Add message with token count for text input
        st.session_state.messages.append({
            "role": "user", 
            "parts": user_input,
            "tokens": len(user_input) // 4
        })
        with st.chat_message("user"):
            st.write(user_input)

        # Trim history to avoid exceeding token limit
        token_limit = 32500  # actually 32767, but conservative
        history = st.session_state.messages
        current_token_count = sum(m.get('tokens', 0) for m in history)
        while current_token_count > token_limit and len(history) > 1:
            # Remove the oldest message
            oldest_message = history.pop(0)
            current_token_count -= oldest_message.get('tokens', 0)

        # Format messages for the model
        formatted_history = []
        for m in history:
            if isinstance(m["parts"], str):
                formatted_history.append({"role": m["role"], "parts": [m["parts"]]})
            else:
                formatted_history.append({"role": m["role"], "parts": [m["parts"]]})

        print("history length:", len(formatted_history)) ### for debugging

        response = None  # Initialize response
        for delay in [5, 10, 20, 30]:
            try:
                response = st.session_state.model.generate_content(formatted_history, stream=True)
                break
            except Exception as e:
                st.error(f"Error occurred: {e}. Retrying in {delay} seconds...")
                sleep(delay)
        if response:
            with st.chat_message("assistant"):
                st.write_stream((chunk.text for chunk in response))

            st.session_state.messages.append({
                "role": "model", 
                "parts": response.text,
                "tokens": response.usage_metadata.candidates_token_count
            })
        else:
            st.error("Failed to reach the LLM after retrying.")
