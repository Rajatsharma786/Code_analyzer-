import streamlit as st
from openai import OpenAI
import os
import re
from dotenv import load_dotenv
from datetime import datetime
import ast
import difflib
import shutil
import subprocess
import html
import tempfile

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI()

def sanitize_code(code):
    code = re.sub(r"\\\s*\n", "\n", code)  # Remove line continuations
    code = re.sub(r"\\", "", code)  # Remove stray backslashes
    return code

st.set_page_config(layout="wide")
st.title("Code Assistant")

# Sidebar
st.sidebar.header("Upload or Link Code Files")
uploaded_files = st.sidebar.file_uploader("Choose code files", type=["py", "r", "js", "java", "cpp"], accept_multiple_files=True)
github_url = st.sidebar.text_input("Paste GitHub Repo URL (Public)")
repo_files = []

# Git clone button
if st.sidebar.button("Clone Repo"):
    try:
        subprocess.run(["git", "--version"], check=True)
        if github_url.strip():
            try:
                temp_dir = tempfile.mkdtemp()
                subprocess.run(["git", "clone", github_url, temp_dir], check=True)
                st.session_state.repo_path = temp_dir
                st.sidebar.success("✅ Repo cloned successfully!")
            except Exception as e:
                st.sidebar.error(f"❌ Failed to clone repo: {e}")
    except FileNotFoundError:
        st.sidebar.error("Git is not installed or not added to system PATH.")

# Combine uploaded files and repo files into one selection list
combined_files = []
if uploaded_files:
    for file in uploaded_files:
        content = file.read().decode("utf-8")
        combined_files.append({"name": file.name, "content": content})

if "repo_path" in st.session_state:
    for root, dirs, files in os.walk(st.session_state.repo_path):
        for file in files:
            if file.endswith((".py", ".r", ".js", ".java", ".cpp")):
                full_path = os.path.join(root, file)
                relative_path = os.path.relpath(full_path, st.session_state.repo_path)
                combined_files.append({"name": relative_path, "path": full_path})

file_names = [f["name"] for f in combined_files]
selected_file = st.selectbox("📂 Select a file to review:", file_names) if file_names else None

if selected_file:
    current = next(f for f in combined_files if f["name"] == selected_file)
    if "content" in current:
        code = sanitize_code(current["content"])
    else:
        with open(current["path"], "r", encoding="utf-8", errors="ignore") as f:
            code = sanitize_code(f.read())

    extension = current["name"].split(".")[-1].lower()
    language_map = {
        "py": "Python",
        "r": "R",
        "js": "JavaScript",
        "java": "Java",
        "cpp": "C++"
    }
    language = language_map.get(extension, "a programming")

    st.markdown(f"### 💬 What would you like help with? ({language})")

    if "show_suggestions" not in st.session_state:
        st.session_state.show_suggestions = False
    if st.button("💡 Show Suggestions"):
        st.session_state.show_suggestions = not st.session_state.show_suggestions

    if st.session_state.show_suggestions:
        col1, col2, col3, col4, col5 = st.columns(5)
        if col1.button("Refactor this code"):
            st.session_state["user_prompt"] = "Refactor this code and fix potential bugs"
        if col2.button("Explain this code"):
            st.session_state["user_prompt"] = "Explain this code"
        if col3.button("Check for security vulnerabilities"):
            st.session_state["user_prompt"] = "Check for security vulnerabilities"
        if col4.button("Summarize what this file does"):
            st.session_state["user_prompt"] = "Summarize what this file does"
        if col5.button("AI-Powered Bug Predictor"):
            st.session_state["user_prompt"] = ("Where could this code break in production?\n"
                                               "Return the following:\n"
                                               "1. 🧩 Bug-prone areas\n"
                                               "2. 📉 Edge cases missed\n"
                                               "3. 🧪 Suggested unit tests")

    user_prompt = st.text_area("✍️ Enter your question or request below:",
                                value=st.session_state.get("user_prompt", ""),
                                height=100)

    if st.button("🔍 Run Analysis"):
        if user_prompt.strip():
            with st.spinner("Analyzing your prompt..."):
                prompt = f"{user_prompt}\n\nHere is the {language} code:\n{code}"
                try:
                    response = client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "system", "content": f"You are a senior {language} developer and code reviewer."},
                            {"role": "user", "content": prompt}
                        ]
                    )
                    reply = response.choices[0].message.content
                    st.success("✅ Response received!")

                    if "refactor" in user_prompt.lower():
                        refactored = reply.split("```python")[-1].split("```", 1)[0] if "```python" in reply else reply
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown("**Original**")
                            st.code(code, language="python")
                        with col2:
                            st.markdown("**Refactored (with Bug Fixes)**")
                            st.code(refactored, language="python")

                        summary_prompt = f"Summarize the following changes made in the refactored version compared to the original. Mention key bug fixes or improvements.\n\nOriginal Code:\n{code}\n\nRefactored Code:\n{refactored}"
                        summary_response = client.chat.completions.create(
                            model="gpt-3.5-turbo",
                            messages=[
                                {"role": "system", "content": "You are a helpful assistant summarizing code differences."},
                                {"role": "user", "content": summary_prompt}
                            ]
                        )
                        summary_text = summary_response.choices[0].message.content

                        st.markdown("### 🔍 Summary of Changes")
                        st.markdown(f"<div style='background-color:#0f172a; padding:10px; border-radius:6px; color:white;'>{summary_text}</div>", unsafe_allow_html=True)
                    else:
                        st.markdown(reply)

                except Exception as e:
                    st.error(f"Error: {e}")
        else:
            st.warning("Please enter a prompt to run.")
else:
    st.info("⬅️ Upload files or paste a GitHub repo URL to get started.")
