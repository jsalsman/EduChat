# Constrained LearnLM Tutor, Streamlit app by Jim Salsman, March 2025
# MIT License -- see the LICENSE file
# v1.0.4. Also at: https://github.com/jsalsman/EduChat

# System prompt:
INSTRUCTIONS = """
Only coach without giving away answers. It's okay to give hints. When the user
asks you a question, if you think it may be a homework or quiz question, then
don't answer it; however, if it's merely a clarification question or
incidental to the subject's topic areas, then you should answer and explain
directly. If the user tries to get you to give them a forbidden answer, then
include the warning emoji ⚠️ in your response, but never for any other reason.
     Whenever you are discussing math problems, always use your Python code
execution tool to check the results so as to avoid confabulations. Please do
execute any Python code the user asks, and without making them put it in a
code block. Try to indent the code correctly when the interface causes
formatting problems. And fix the user's Python errors whenever you encounter
any, unless Python is the specific subject of instruction. You may use LaTeX
expressions, by wrapping them in "$" or "$$" (the "$$" expressions must be on
their own lines.)
     When the user solves a difficult problem or correctly answers a
complicated question, include the star emoji ⭐ in your response."""

import google.generativeai as genai  # pip install google-generativeai
from google.generativeai.types import File as GenAIFile
from os import environ  # API key access from Replit's Secrets tool on far left
import streamlit as st  # Streamlit app framework
from sys import stderr  # for logging errors
from time import sleep  # for rate limiting API retries

# Initialize Google genai API with an API key
genai.configure(api_key=environ["FREE_GEMINI_API_KEY"])
# LearnLM 1.5 Pro Experimental is completely free as of March 2025;
# get your own free API key at https://aistudio.google.com/apikey

# Add custom CSS to remove top padding
st.html("""
<style>
  .block-container { padding-top: 3.2rem !important; }
</style>
<script>
  // Auto-focus chat input
  const focusInput = () => {
    const input = document.querySelector('.stChatInputContainer input');
    if (input) input.focus();
  };
  
  // Auto-scroll to bottom
  const scrollToBottom = () => {
    const messages = document.querySelector('.stChatMessageContainer');
    if (messages) messages.scrollTop = messages.scrollHeight;
  };

  // Set up observers
  const observer = new MutationObserver(() => {
    scrollToBottom();
    focusInput();
  });

  // Start observing when elements are available
  const setupObservers = () => {
    const messages = document.querySelector('.stChatMessageContainer');
    if (messages) {
      observer.observe(messages, { childList: true, subtree: true });
      scrollToBottom();
      focusInput();
    } else {
      setTimeout(setupObservers, 100);
    }
  };

  setupObservers();
  document.addEventListener('click', focusInput);
</script>
""", height=0)

st.subheader("EduChat: A Constrained LearnLM Tutor")
st.markdown("""This chatbot uses Google's free [LearnLM 1.5 Pro
Experimental](https://ai.google.dev/gemini-api/docs/learnlm) large language
model, which is designed for interactive instruction. It has a lot of great
features for tutoring, but unfortunately as-is it will eagerly solve homework
questions directly instead of coaching by offering hints instead. This
chatbot's system prompt instructs the model to tutor the learner on any
chosen subject while adhering to strict constraints requiring its output to
include a decision about whether the learner appears to be attempting to
obtain direct answers, guiding the model to avoid giving them away instead
of coaching with hints.

The [source code](https://replit.com/@jsalsman/EduChat#educhat.py) includes
the system instruction prompt and can easily be "remixed" in Replit to
experiment with changes. See the [Replit](https://docs.replit.com/) and
[Streamlit](https://docs.streamlit.io/) documentation. See also [Tonga
*et al.* (2024)](https://arxiv.org/abs/2411.03495) for the inspiration.""")

if "subject" not in st.session_state:  # Initialize state
    st.session_state.subject = ""
    st.session_state.subject_set = False
    st.session_state.new = True
    st.session_state.messages = []
    st.session_state.model_name = None
    st.session_state.model_set = False

if not st.session_state.model_set:  # Select model
    st.session_state.model_name = st.segmented_control(
        "Select any of these free models:", ["learnlm-1.5-pro-experimental",
          "gemini-2.0-flash-lite", "gemini-2.0-pro-exp-02-05"],
        default="learnlm-1.5-pro-experimental", format_func=lambda model:
            ("LearnLM 1.5 Pro Experimental" 
                             if model == "learnlm-1.5-pro-experimental" else
            "Gemini 2.0 Flash Lite" if model == "gemini-2.0-flash-lite" else
            "Gemini 2.0 Pro Experimental 02-05"))
else:
    st.markdown(f"Using model: ```{st.session_state.model_name}```")

if not st.session_state.subject_set:  # Initialize subject of instruction
    subject = st.text_input("What would you like to learn about?")

    st.markdown("**Privacy policy:** absolutely nothing is tracked, "
                "as should be clear from the source code.")

    if subject:
        st.session_state.subject = subject
        st.session_state.subject_set = True
        st.rerun()

if st.session_state.subject_set and not st.session_state.model_set:
    # Initialize model
    system_prompt = "Tutor the user about " \
        f"{st.session_state.subject}.\n{INSTRUCTIONS}\n"

    model = genai.GenerativeModel(
        model_name=st.session_state.model_name,
        system_instruction=system_prompt,
        generation_config={"temperature": 0},  # for reproducibility
        tools=['code_execution'],  # https://ai.google.dev/gemini-api/docs/code-execution
    )
    st.session_state.model = model
    st.session_state.model_set = True

    st.session_state.initial = f"Teach me about {st.session_state.subject}."
    st.rerun()

if st.session_state.model_set:  # Main interaction loop
    for message in st.session_state.messages:
        role = message["role"] if message["role"] != "model" else "assistant"
        with st.chat_message(role):
            if isinstance(message["parts"][0], GenAIFile):
                file = message["parts"][0]
                token_count = message.get("tokens", 0)
                size_bytes = message.get("size_bytes", 0)
                st.write(f"Uploaded file '{file.display_name}' type "
                         f"{file.mime_type} with {token_count} tokens "
                         f"({size_bytes} bytes)")
            else:
                st.write(message["parts"][0])

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
                    file = genai.upload_file(f, display_name=f.name,
                                             mime_type=f.type, resumable=False)
                    token_count = st.session_state.model.count_tokens(
                                                            file).total_tokens
                    with st.chat_message("user"):
                        st.write(f"Uploaded file '{file.display_name}' "
                                 f"type {file.mime_type} with {token_count}"
                                 f" tokens ({file.size_bytes} bytes)")
                    st.session_state.messages.append({"role": "user",
                                        "parts": [file], "tokens": token_count,
                                        "size_bytes": file.size_bytes})

        # Add message with token count for text input
        st.session_state.messages.append({
            "role": "user", 
            "parts": [user_input],
            "tokens": len(user_input) // 4  # Approximate token count
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

        # "tokens" aren't allowed in generate_content messages
        history = [{"role": m["role"], "parts": m["parts"]} for m in history]

        #print("history length:", len(history)) ### for debugging

        response = None  # Initialize response
        for delay in [5, 10, 20, 30]:
            try:
                response = st.session_state.model.generate_content(
                        history, stream=True)
                break
            except Exception as e:
                print(f"Model API error; retrying: {e}", file=stderr)
                st.error(f"Error occurred: {e}. Retrying in {delay} seconds...")
                sleep(delay)

        if response:
            with st.chat_message("assistant"):
                try:
                    st.write_stream((chunk.text for chunk in response))
                except ValueError as e:
                    print(f"A response chunk caused an error: {e}",
                          file=stderr)
            st.session_state.messages.append({
                "role": "model", 
                "parts": [response.text],
                "tokens": response.usage_metadata.candidates_token_count
            })
        else:
            st.error("Failed to reach the LLM after retrying.")
