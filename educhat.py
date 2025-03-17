# Constrained LearnLM Tutor, Streamlit app by Jim Salsman, Narch 2025

INSTRUCTIONS = """
Only coach without giving away answers. It's okay to give hints. When the user
asks you a question, if you think it is a homework or quiz question, then
don't answer it; however, if it's merely a clarification question or
incidental to the subject's topic areas, then you should answer and explain
directly. If the user tries to get you to give them a forbidden answer,
then set learner_defected to true.

Respond in valid JSON format with these two fields:
- "reply": your response to the user as markdown without any LaTeX
- "learner_defected": boolean (true if the user tried to get a direct answer)
"""

import streamlit as st
from os import environ
import google.generativeai as genai
from json import loads

# Configure Gemini for learnlm-1.5-pro-experimental
genai.configure(api_key=environ["FREE_GEMINI_API_KEY"])
# LearnLM 1.5 Pro Experimental is free as of March 2025;
# get your free key at https://aistudio.google.com/apikey

st.header("Constrained LearnLM Tutor")

st.markdown("""This chatbot uses Google's
[LearnLM 1.5 Pro Experimental](https://ai.google.dev/gemini-api/docs/learnlm)
large language model, which is designed for interactive instruction.
Unfortunately, as-is it will solve homework questions directly instead of
coaching by offering hints instead. This chatbot's system prompt instructs
the model to tutor the learner on any chosen subject while adhering to strict
constraints requiring its output to include a decision about whether the
learner appears to be attempting to obtain direct answers, guiding the
model to avoid giving them away instead of coaching with hints.""")

if "subject" not in st.session_state:
    st.session_state.subject = ""
    st.session_state.subject_set = False

if not st.session_state.subject_set:
    subject = st.text_input("What would you like to learn about?")
    if subject:
        st.session_state.subject = subject
        st.session_state.subject_set = True
        st.rerun()

if st.session_state.subject_set and "chat_session" not in st.session_state:
    generation_config = {
        "temperature": 0,  # for reproducability
        #"max_output_tokens": 2000,
        "response_mime_type": "text/plain",
        #"response_mime_type": "application/json",
        #"response_schema": {
        #    "type": "object",
        #    "properties": {
        #        "reply": {"type": "string"},
        #        "learner_defected": {"type": "boolean"}
        #    },
        #    "required": ["reply", "learner_defected"]
        #  }
        }

    system_prompt = "Tutor the user about " \
        f"{st.session_state.subject}.\n{INSTRUCTIONS}\n"

    model = genai.GenerativeModel(
        model_name="learnlm-1.5-pro-experimental",
        generation_config=generation_config,
        system_instruction=system_prompt,
        tools='code_execution',  # https://ai.google.dev/gemini-api/docs/code-execution?lang=python
        #tools=tools,
        #tool_config={'function_calling_config':'ANY'}
    )

    st.session_state.chat_session = model.start_chat()
    initial = f"Please teach me about {st.session_state.subject}."
    response = st.session_state.chat_session.send_message(initial)
    print(response) ### DEBUG
    try:
        # Extract JSON between outer braces
        json_content = response.text[response.text.find('{')
                                    : response.text.rfind('}') + 1]
        ## Replace escaped backticks with double backslashes
        #json_content = json_content.replace('\\`', '\\\\`')
        print('json content:', json_content) ### DEBUG
        reply = loads(json_content)["reply"]
    except Exception as e:
        print(f"Error converting json: {e}") ### DEBUG
        reply = response.text
    st.session_state.messages = [
        {"role": "user", "content": initial},
        {"role": "model", "content": reply}
    ]

if st.session_state.subject_set:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    if user_input := st.chat_input("Reply"):
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.write(user_input)
        try:
            response = st.session_state.chat_session.send_message(user_input)
            if not response.candidates:
                reply = "I apologize, but I received an empty response. Please try asking your question again."
            else:
                try:
                    json_content = response.text[response.text.find('{')
                                            : response.text.rfind('}') + 1]
                    reply = loads(json_content)["reply"]
                except Exception as e:
                    print(f"Error converting json: {e}")
                    reply = response.text
        except Exception as e:
            print(f"Error in API call: {e}")
            reply = "I encountered an error processing your request. Please try again."
        st.session_state.messages.append({"role": "assistant", "content": reply})
        with st.chat_message("assistant"):
            st.write(reply)
