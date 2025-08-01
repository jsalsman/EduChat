# Constrained LearnLM Tutor, Streamlit app by Jim Salsman, March-July 2025
# MIT License -- see the LICENSE file
VERSION="2.0.1"  # upgraded to the new genai API
# For stable releases see: https://github.com/jsalsman/EduChat

# System prompt suffix:
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

import google.genai as genai  # pip install google-genai
from google.genai.types import Part, Content, File as GenAIFile
from os import environ  # API key access from secrets, and host name
import streamlit as st  # Streamlit app framework
from streamlit_cookies_manager_ext import EncryptedCookieManager
from sys import stderr  # for logging errors
from time import sleep  # for rate limiting API retries

# Using one cookie to permanently dismiss the modal dialog announcement
cookies = EncryptedCookieManager(prefix="educhat/",
                                 password="not confidential")
if not cookies.ready():
    st.stop()

st.subheader("EduChat: A Constrained LearnLM Tutor")
st.markdown("""This chatbot uses Google's free
[LearnLM](https://ai.google.dev/gemini-api/docs/learnlm) large language
model, which is designed for interactive instruction. It has a lot of great
features for tutoring, but unfortunately as-is it will eagerly solve homework
questions directly instead of coaching by offering hints instead. This
chatbot's system prompt instructs the model to tutor the learner on any
chosen subject while adhering to strict constraints requiring its output to
include a decision about whether the learner appears to be attempting to
obtain direct answers, guiding the model to avoid giving them away instead
of coaching with hints.

The [source code](https://github.com/jsalsman/EduChat/blob/main/educhat.py)
includes the full system prompt. [The GitHub
repo](https://github.com/jsalsman/EduChat) can be forked and deployed entirely
for free on the [Streamlit Community Cloud](https://share.streamlit.io/)
to experiment with changes; see the [Streamlit
docs](https://docs.streamlit.io/). See also [Tonga *et al.*
(2024)](https://arxiv.org/abs/2411.03495) for the inspiration. [Please
consider donating](https://paypal.me/jsalsman) to support this work.

**NOTE:** There is a transient Google genai API bug which sometimes
supresses the first response from the model. You can proceed normally
by typing a question mark and pressing Enter.""")

@st.dialog("EduChat has moved to the Streamlit Community Cloud")
def dialog():
    st.write("Due the unexpected viral popularity of this web app, my "
             "Replit hosting bill blew up since its announcement. "
             "So now its hostname is ```edu-chat.streamlit.app``` "
             "because the Streamlit Community Cloud provides an "
             "equivalent service at no cost.")
    st.write("Please consider [donating a few "
             "dolars](https://paypal.me/jsalsman) to support this work "
             "and help cover my surprise Replit charges.")
    st.write("This move makes it even easier to experiment with changes, "
             "by forking [the GitHub Repo]"
             "(https://github.com/jsalsman/EduChat) and [deploying your "
             "fork](https://share.streamlit.io/) entirely for free. "
             "Thank you for your understanding and consideration.")
    st.session_state.dialog = 'seen'
    if st.button("Don't show this again."):
        cookies['dialog'] = 'seen'
        st.rerun()
if ("dialog" not in st.session_state and cookies.get('dialog', '') != 'seen'):
    dialog()

# LearnLM 1.5 Pro Experimental is completely free as of March 2025;
# get your own free API key at https://aistudio.google.com/apikey

# Initialize the Google genai API with an API key
if 'key_set' not in st.session_state:
    try:
        # Create client with API key
        client = genai.Client(api_key=environ["GEMINI_API_KEY"])
        # Test the client by listing models
        models = list(client.models.list())
        print("models:", len(models), file=stderr)
        st.session_state.client = client
        st.session_state.key_set = True
    except:
        st.error("API key not found or invalid. Please [get your own free "
                 "API key.](https://aistudio.google.com/apikey)")
        def clear_api_key():
            st.session_state.apikey = ""
        api_key_input = st.text_input("Paste your Gemini API key here: (or "
                 "add it as a secret GEMINI_API_KEY environment variable)",
                 key="apikey", placeholder="API key", type="password",
                 on_change=clear_api_key())
        if api_key_input:
            try:
                client = genai.Client(api_key=api_key_input)
                test_response = client.models.generate_content(
                    model='gemini-2.0-flash',
                    contents='Hello, world!'
                )
                print("API test successful", file=stderr)
                st.session_state.client = client
                st.session_state.key_set = True
            except Exception as e:
                print(f"Bad API key: {e}")
            st.rerun()

if "subject" not in st.session_state:  # Initialize state
    st.session_state.subject = ""
    st.session_state.subject_set = False
    st.session_state.new = True
    st.session_state.messages = []
    st.session_state.model_name = None
    st.session_state.model_set = False
    st.session_state.chat = None

if not st.session_state.model_set:  # Select model
    st.session_state.model_name = st.segmented_control(
        "Select any of these free models:", ["learnlm-2.0-flash-experimental",
          "gemini-2.5-flash", "gemini-2.5-flash-lite"],
        default="learnlm-2.0-flash-experimental", format_func=lambda model:
            ("LearnLM 2.0 Flash Experimental" 
                             if model == "learnlm-2.0-flash-experimental" else
            "Gemini 2.5 Flash" if model == "gemini-2.5-flash" else
            "Gemini 2.5 Flash Lite"))
else:
    st.markdown(f"Using model: ```{st.session_state.model_name}```")

if not st.session_state.subject_set:  # Initialize subject of instruction
    subject = st.text_input("What would you like to learn about?",
                            placeholder="General subject or specific topic")

    st.markdown("**Privacy policy:** No identifying information or any chat "
                f"messages are ever recorded. Verson {VERSION}.")

    if subject:
        st.session_state.subject = subject
        st.session_state.subject_set = True
        st.rerun()

if st.session_state.subject_set and not st.session_state.model_set:
    # Initialize chat with system prompt
    system_prompt = "Tutor the user about " \
        f"{st.session_state.subject}.\n{INSTRUCTIONS}\n"  # append suffix above

    # Create config for the chat
    config = types.GenerateContentConfig(
        system_instruction=system_prompt,
        temperature=0,  # for reproducibility
        tools=[{"code_execution": {}}]  # Enable code execution
    )
    
    # Create a new chat session with the client
    chat = st.session_state.client.chats.create(
        model=st.session_state.model_name,
        config=config
    )
    st.session_state.chat = chat
    st.session_state.model_set = True

    st.session_state.initial = f"Teach me about {st.session_state.subject}."
    st.rerun()

if st.session_state.model_set:  # Main interaction loop
    for message in st.session_state.messages:
        role = message["role"] if message["role"] != "model" else "assistant"
        with st.chat_message(role):
            if "file_info" in message:
                file_info = message["file_info"]
                st.write(f"Uploaded file '{file_info['display_name']}' type "
                         f"{file_info['mime_type']} with {file_info['tokens']} tokens "
                         f"({file_info['size_bytes']} bytes)")
            else:
                st.write(message["text"])

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
                    # Upload file to the client (using bytes instead of path)
                    file_bytes = f.read()
                    file = st.session_state.client.files.upload(
                        file=file_bytes, 
                        display_name=f.name,
                        mime_type=f.type
                    )
                    # Get token count (this might need adjustment based on new API)
                    # For now, we'll estimate based on file size
                    token_count = len(file_bytes) // 4  # Rough estimate
                    
                    with st.chat_message("user"):
                        st.write(f"Uploaded file '{file.display_name}' "
                                 f"type {file.mime_type} with ~{token_count}"
                                 f" tokens ({len(file_bytes)} bytes)")
                    st.session_state.messages.append({
                        "role": "user",
                        "file_info": {
                            "display_name": file.display_name,
                            "mime_type": file.mime_type,
                            "tokens": token_count,
                            "size_bytes": len(file_bytes),
                            "file": file
                        },
                        "tokens": token_count
                    })

        # Add text message with token count
        st.session_state.messages.append({
            "role": "user", 
            "text": user_input,
            "tokens": len(user_input) // 4  # Approximate token count
        })
        with st.chat_message("user"):
            st.write(user_input)

        # Trim history to avoid exceeding token limit
        token_limit = 32500  # actually 32767 for LearnLM, but conservative
        history = st.session_state.messages
        current_token_count = sum(m.get('tokens', 200) for m in history)
        while current_token_count > token_limit and len(history) > 1:
            # Remove the oldest message
            oldest_message = history.pop(0)
            current_token_count -= oldest_message.get('tokens', 0)

        # Send message to chat
        response = None  # Initialize response
        for delay in [5, 10, 20, 30]:
            try:
                # Send the message using the new API
                response = st.session_state.chat.send_message(user_input)
                break
            except Exception as e:
                print(f"Model API error; retrying: {e}", file=stderr)
                st.error(f"Error: {e}. Retrying in {delay} seconds...")
                sleep(delay)
        
        if response:
            # Display the response (handle both streaming and non-streaming)
            with st.chat_message("assistant"):
                response_text = ""
                
                # Check if response has text attribute directly
                if hasattr(response, 'text'):
                    response_text = response.text
                    st.write(response_text)
                else:
                    # Handle other response formats
                    try:
                        # Try to get text from candidates
                        if hasattr(response, 'candidates') and response.candidates:
                            response_text = response.candidates[0].content.parts[0].text
                            st.write(response_text)
                    except Exception as e:
                        print(f"Response handling error: {e}", file=stderr)
                        response_text = "Error processing response"
                        st.write(response_text)
            
            # Calculate token count for response
            response_tokens = len(response_text) // 4  # Approximate
            
            st.session_state.messages.append({
                "role": "model", 
                "text": response_text,
                "tokens": response_tokens
            })
            st.rerun()
        else:
            st.error("Failed to reach the LLM after four retries. Wait a few "
                     "minutes and repeat your reply, or, to avoid these rate "
                     "limiting problems, [fork the GitHub repo]"
                     "(https://github.com/jsalsman/EduChat), create [your "
                     "own Gemini API key](https://aistudio.google.com/apikey), "
                     "and deploy your fork on the [Streamlit Community cloud]"
                     "(https://share.streamlit.io/).")
