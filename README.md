
# EduChat: A Constrained LearnLM Tutor

[![Run on Streamlit Community Cloud](https://img.shields.io/badge/Run_on_Streamlit_Community_Cloud-darkgreen)](https://edu-chat.streamlit.app)
[![Google Genai Version](https://img.shields.io/badge/google--genai-0.8-blue)](https://googleapis.github.io/python-genai/)
[![Streamlit Version](https://img.shields.io/badge/sreamlit-1.43-blue)](https://streamlit.io/)
[![Python Version](https://img.shields.io/badge/python-3.10-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

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

MIT License - See the LICENSE file for details

## Contributing

Feel free to fork this repo and customize it, and deploy entirely for free on the [Streamlit Community Cloud](https://share.streamlit.io/).

## Program Logic

The program follows this logical sequence:

1. **Initial Setup** (Lines 1-40):
   - Defines the system instructions for the tutor
   - Imports required libraries
   - Configures Google's GenerativeAI with API key
   - Sets up Streamlit interface styling

2. **State Management** (Lines 41-47):
   - Initializes session state variables for:
     - Subject of study
     - New session flag
     - Message history
     - Model selection state

3. **Model Selection** (Lines 48-58):
   - Provides a segmented control to select between different LLM models
   - Displays current model selection

4. **Subject Initialization** (Lines 59-69):
   - Prompts user for learning subject
   - Includes privacy policy
   - Triggers rerun when subject is set

5. **Model Initialization** (Lines 70-88):
   - Creates system prompt combining subject and instructions
   - Configures model with:
     - Zero temperature for consistency
     - Code execution capability
   - Sets up initial teaching prompt

6. **Main Interaction Loop** (Lines 89-184):
   - Displays message history
   - Handles file uploads
   - Manages token limits
   - Processes user input
   - Generates and streams AI responses
   - Includes error handling and retry logic
   - Updates conversation history

7. **Token Management** (Lines 128-137):
   - Tracks token usage
   - Trims conversation history to prevent exceeding limits
   - Maintains approximate token counts

8. **Error Handling** (Lines 150-184):
   - Implements exponential backoff for API retries
   - Provides user feedback for errors
   - Handles response streaming failures

The program uses Streamlit's session state to maintain conversation context and Google's GenerativeAI API for response generation, while enforcing educational constraints through the system prompt.
