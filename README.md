
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

1. Fork this repo to create your own instance
2. Add your Google API key in the Secrets tool (Environment Variables) with the key name `FREE_GEMINI_API_KEY`
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

Feel free to fork this repo and customize it for your own educational purposes!
