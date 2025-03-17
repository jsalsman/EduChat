
import streamlit as st
import os
import google.generativeai as genai
from google.ai.generativelanguage_v1beta.types import content

# Configure Gemini
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

# Initialize session state for chat history
if "chat_session" not in st.session_state:
    generation_config = {
        "temperature": 0,
        "top_p": 0.95,
        "top_k": 64,
        "max_output_tokens": 8192,
        "parameters": genai.protos.Schema(
            type=genai.protos.Type.OBJECT,
            required=["reply", "learner_defected"],
            properties={
                "reply": genai.protos.Schema(
                    type=genai.protos.Type.STRING,
                ),
                "learner_defected": genai.protos.Schema(
                    type=genai.protos.Type.BOOLEAN,
                ),
            },
        ),
        "response_mime_type": "application/json",
    }

    model = genai.GenerativeModel(
        model_name="learnlm-1.5-pro-experimental",
        generation_config=generation_config,
        system_instruction="Tutor the learner on this subject: Electromagnetism and Maxwell's equations\n\nRespond using the reply field. Only coach without giving away answers. It's okay to give hints. If the learner tries to get you to give them the answer, then set the learner_defected boolean to true.",
    )

    st.session_state.chat_session = model.start_chat()
    # Send initial message
    response = st.session_state.chat_session.send_message("begin")
    st.session_state.messages = [{"role": "assistant", "content": eval(response.text)["reply"]}]

st.title("Physics Tutor Bot")

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Chat input
if user_input := st.chat_input("Ask your question about electromagnetism"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Display user message
    with st.chat_message("user"):
        st.write(user_input)
    
    # Get bot response
    response = st.session_state.chat_session.send_message(user_input)
    response_data = eval(response.text)
    
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response_data["reply"]})
    
    # Display assistant response
    with st.chat_message("assistant"):
        st.write(response_data["reply"])
        if response_data["learner_defected"]:
            st.warning("Please try to solve the problem yourself instead of asking for direct answers.")
