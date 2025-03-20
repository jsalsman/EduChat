
# EduChat: A Constrained LearnLM Tutor

[![Run on Streamlit Community Cloud](https://img.shields.io/badge/Run_on-Streamlit_Community_Cloud-darkgreen?logo=streamlit)](https://edu-chat.streamlit.app)
[![Google Genai Version](https://img.shields.io/badge/google--genai-0.8-blue)](https://googleapis.github.io/python-genai/)
[![Streamlit Version](https://img.shields.io/badge/sreamlit-1.43-blue)](https://streamlit.io/)
[![Python Version](https://img.shields.io/badge/python-3.10-blue)](https://www.python.org/downloads/)
[![MIT License](https://img.shields.io/badge/License-MIT-yellow)](https://opensource.org/licenses/MIT)
[![Donate](https://img.shields.io/badge/Donate-gold?logo=paypal)](https://paypal.me/jsalsman)

EduChat is a Streamlit-based educational chatbot that leverages Google's LearnLM 1.5 Pro Experimental large language model for interactive tutoring. The chatbot is designed to provide guided learning experiences while avoiding direct answers to homework questions.

## Usage

1. When you first run the app, select your preferred model
2. Enter the subject you want to learn about
3. Start asking questions and interacting with the tutor
4. The tutor will provide hints and guidance rather than direct answers
5. Look for special emoji indicators:
   - ⚠️ Warns when attempting to get forbidden answers
   - ⭐ Appears when correctly solving difficult problems

## Features

- Interactive tutoring on any subject
- Built-in Python code execution capabilities
- Support for LaTeX mathematical expressions
- File upload functionality
- Instructional hints instead of direct answers
- Multiple model options:
  - LearnLM 1.5 Pro Experimental
  - Gemini 2.0 Flash Lite
  - Gemini 2.0 Pro Experimental 02-05

## Privacy

The application does not track or store any user data or conversations.

## Source code

The Streamlit/Python source code is entirely in the [educhat.py](educhat.py) file. No other files are usually necessary to run it.

## Deploying Your Own Fork

1. Fork this GitHub repo and deploy your fork on the [Streamlit Community Cloud](https://share.streamlit.io/).
2. For "Main file path" use `educhat.py`.
3. Under "Advanced settings" ensure that Python 3.10 is selected, and under Secrets, add your [free API key](https://aistudio.google.com/apikey) in the format `GEMINI_API_KEY="your API key"`.
4. Click the "Deploy" button to launch your customized Streamlit app.

## Requirements

The project uses Poetry for dependency management, but includes a `requirements.txt` file for `pip`. Key dependencies include:
- Python 3.10
- Streamlit 1.43
- Google GenerativeAI 0.8

## Credits

- Implementation by Jim Salsman, March 2025
- Inspired by [Tonga et al. (2024)](https://arxiv.org/abs/2411.03495)

## License

MIT License - See the [LICENSE](LICENSE) file for details.

## Contributing

Feel free to fork this repo and customize it, and deploy entirely for free on the [Streamlit Community Cloud](https://share.streamlit.io/).

## Program Logic
1. **Initial Setup** (Lines 1-56):
   - Defines the system instructions for the tutor (Lines 7-23)
   - Imports required libraries (Lines 25-30)
   - Configures Streamlit interface styling (Lines 32-35)
   - Sets up app header and description (Lines 37-56)

2. **Streamlit Dialog for Migration** (Lines 58-76):
   - Provides notification about migration from Replit to Streamlit Cloud
   - Includes donation requests and continuation options

3. **API Key Configuration** (Lines 81-105):
   - Attempts to configure Google's GenerativeAI with environment variable API key
   - Provides fallback for manual API key entry
   - Includes error handling for invalid keys

4. **State Management** (Lines 107-114):
   - Initializes session state variables for:
     - Subject of study
     - New session flag
     - Message history
     - Model selection state

5. **Model Selection** (Lines 115-126):
   - Provides options to select different LLM models
   - Displays current model selection when set

6. **Subject Initialization** (Lines 127-138):
   - Prompts user for learning subject
   - Includes privacy policy and version information
   - Triggers rerun when subject is set

7. **Model Initialization** (Lines 139-155):
   - Creates system prompt combining subject and instructions
   - Configures model with:
     - Zero temperature for consistency
     - Code execution capability
   - Sets up initial teaching prompt

8. **Main Interaction Loop** (Lines 157-238):
   - Displays message history (Lines 158-169)
   - Handles chat input and file uploads (Lines 171-192)
   - Adds user messages to history (Lines 193-200)
   - Manages token limits (Lines 202-212)
   - Processes API requests with retry logic (Lines 214-224)
   - Generates and streams AI responses (Lines 225-236)
   - Includes error handling (Lines 221-223, 229-231, 238-245)

The program uses Streamlit's session state to maintain conversation context and Google's GenerativeAI API for response generation, while enforcing educational constraints through the system prompt defined at the beginning of the file.
