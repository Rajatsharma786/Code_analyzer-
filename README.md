# Code Assistant
**An AI-powered, multi-language code review and debugging assistant built with Streamlit and OpenAI.**

This project enables developers to review, refactor, and analyze source code using natural language prompts—directly in the browser. It supports multi-file uploads, GitHub repository integration, and languages including Python, JavaScript, R, Java, and C++.

## Key Features

- Upload multiple source files or paste a public GitHub repository URL  
- Select and analyze files with human-friendly prompts  
- Generate on-demand:
  - Refactored code
  - Security insights
  - Unit tests
  - File/function-level summaries
- Toggleable smart suggestion bar to assist with prompt creation
- Clean interface with persistent chat history and time tracking

## Technology Stack

- **Frontend:** Streamlit  
- **LLM Integration:** OpenAI API  
- **Supported Languages:** Python, JavaScript, R, Java, C++  
- **Other Tools:** Git, dotenv, Radon, difflib

## Getting Started

1. **Clone the repository**
```bash
git clone https://github.com/your-username/code-assistant.git
cd code-assistant
```

2. **Set up your environment**
```bash
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

3. **Add your OpenAI API key**
Create a `.env` file in the root directory:
```
OPENAI_API_KEY=your_openai_key_here
```

4. **Launch the application**
```bash
streamlit run app.py
```

## Planned Enhancements

- Repository-level diff view  
- Local model fallback integration (e.g., HuggingFace)  
- UI themes (dark/light mode)  
- Batch test generation  
- Performance benchmarking across files

## Author

Developed by [Your Name] to explore practical applications of large language models in real-time code analysis and review.  
For feedback, contributions, or collaboration opportunities, feel free to connect on [LinkedIn](https://www.linkedin.com/in/yourprofile).
