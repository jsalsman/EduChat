
import streamlit as st
import os
import google.generativeai as genai
from google.ai.generativelanguage_v1beta.types import content

# Configure Gemini
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

st.title("EduChat Tutor Bot")

# Initialize subject in session state
if "subject" not in st.session_state:
    st.session_state.subject = ""
    st.session_state.subject_set = False

# Ask for subject if not set
if not st.session_state.subject_set:
    subject = st.text_input("What subject would you like to learn about?")
    if subject:
        st.session_state.subject = subject
        st.session_state.subject_set = True
        st.rerun()

# Initialize chat after subject is set
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
    - "reply": your response to the learner
    - "learner_defected": boolean (true if learner is trying to get direct answers)
    """

    st.session_state.chat_session = model.start_chat(history=[
        {"role": "user", "parts": [f"I want to learn about {st.session_state.subject}"]},
        {"role": "model", "parts": [system_prompt]}
    ])
    
    response = st.session_state.chat_session.send_message(f"I want to learn about {st.session_state.subject}")
    response_text = response.text.strip()
    
    # Remove any potential prefix (like "EduChat Tutor Bot")
    if "\n" in response_text:
        response_text = response_text.split("\n")[-1].strip()
    
    # Try to extract just the JSON part
    try:
        import json
        json_start = response_text.find('{')
        json_end = response_text.rfind('}') + 1
        if json_start >= 0 and json_end > json_start:
            json_str = response_text[json_start:json_end]
            response_data = json.loads(json_str)
            st.session_state.messages = [{"role": "assistant", "content": response_data["reply"]}]
        else:
            st.session_state.messages = [{"role": "assistant", "content": response_text}]
    except:
        st.session_state.messages = [{"role": "assistant", "content": response_text}]

# Display chat interface once subject is set
if st.session_state.subject_set:
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # Chat input
    if user_input := st.chat_input("Reply"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        # Display user message
        with st.chat_message("user"):
            st.write(user_input)
        
        # Get bot response
        response = st.session_state.chat_session.send_message(user_input)
        
        response_text = response.text.strip()
        
        # Remove any potential prefix
        if "\n" in response_text:
            response_text = response_text.split("\n")[-1].strip()
        
        try:
            import json
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                response_data = json.loads(json_str)
                reply_content = response_data["reply"]
                learner_defected = response_data.get("learner_defected", False)
            else:
                reply_content = response_text
                learner_defected = False
        except:
            reply_content = response_text
            learner_defected = False
        
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": reply_content})
        
        # Display assistant response
        with st.chat_message("assistant"):
            st.write(reply_content)
            if learner_defected:
                st.warning("Please try to solve the problem yourself instead of asking for direct answers.")
