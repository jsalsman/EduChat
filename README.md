
# EduChat: A Constrained LearnLM Tutor

EduChat is a Streamlit-based educational chatbot that leverages Google's LearnLM 1.5 Pro Experimental large language model for interactive tutoring. The chatbot is designed to provide guided learning experiences while avoiding direct answers to homework questions.

## Source code

The source code is entirely in the [educhat.py](educhat.py) file. None of the other files are necessary to run it outside of Replit.

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

## Getting Started

1. Visit the [Replit app](https://replit.com/@jsalsman/EduChat) and click "Remix this app", or fork this GitHub repo to create your own instance
2. Add your own Google API key in Replit's Secrets tool (environment variables) with the key name `FREE_GEMINI_API_KEY`
3. Click the "Run" button to start the Streamlit app

## Requirements

The project uses Poetry for dependency management. Key dependencies include:
- Python 3.10
- Streamlit
- Google GenerativeAI

## Usage

1. When you first run the app, select your preferred model
2. Enter the subject you want to learn about
3. Start asking questions and interacting with the tutor
4. The tutor will provide hints and guidance rather than direct answers
5. Look for special emoji indicators:
   - ⚠️ Warns when attempting to get forbidden answers
   - ⭐ Appears when correctly solving difficult problems

## Privacy

The application does not track or store any user data or conversations.

## License

MIT License - See the LICENSE file for details

## Credits

- Implementation by Jim Salsman, March 2025
- Inspired by [Tonga et al. (2024)](https://arxiv.org/abs/2411.03495)

## Contributing

Feel free to fork this repo and customize it.

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
