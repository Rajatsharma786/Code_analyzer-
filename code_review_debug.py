import streamlit as st
from openai import OpenAI
import os
import re
from dotenv import load_dotenv
from datetime import datetime
import ast
import difflib
import tempfile
import shutil
import subprocess

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI()

def sanitize_code(code):
    code = re.sub(r"\\\s*\n", "\n", code)  # Remove line continuations
    code = re.sub(r"\\", "", code)  # Remove stray backslashes
    return code

def show_diff(original, suggestion):
    original_lines = original.splitlines(keepends=False)
    suggestion_lines = suggestion.splitlines(keepends=False)
    diff = difflib.ndiff(original_lines, suggestion_lines)
    html_diff = "<pre style='font-size:13px;background:#0f172a;color:#f8fafc;padding:10px;border-radius:8px;'>"
    for line in diff:
        if line.startswith('+'):
            html_diff += f"<span style='color:#22c55e;'>{line}</span>\n"
        elif line.startswith('-'):
            html_diff += f"<span style='color:#ef4444;'>{line}</span>\n"
        elif line.startswith('?'):
            continue
        else:
            html_diff += f"{line}\n"
    html_diff += "</pre>"
    return html_diff

st.set_page_config(layout="wide")
st.title("Code Assistant")

# Sidebar
st.sidebar.header("Upload or Link Code Files")
uploaded_files = st.sidebar.file_uploader("Choose code files", type=["py", "r", "js", "java", "cpp"], accept_multiple_files=True)
github_url = st.sidebar.text_input("Paste GitHub Repo URL (Public)")

repo_files = []
if github_url.strip():
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            subprocess.run(["git", "clone", github_url, tmpdir], check=True)
            for root, dirs, files in os.walk(tmpdir):
                for file in files:
                    if file.endswith((".py", ".r", ".js", ".java", ".cpp")):
                        path = os.path.join(root, file)
                        with open(path, "r", encoding="utf-8", errors="ignore") as f:
                            content = f.read()
                            repo_files.append({"name": os.path.relpath(path, tmpdir), "content": content})
        st.sidebar.success("✅ Repo cloned successfully!")
    except Exception as e:
        st.sidebar.error(f"❌ Failed to clone repo: {e}")

# Combine all files into one selection list
combined_files = []
if uploaded_files:
    for file in uploaded_files:
        content = file.read().decode("utf-8")
        combined_files.append({"name": file.name, "content": content})
if repo_files:
    combined_files.extend(repo_files)

file_names = [f["name"] for f in combined_files]
selected_file = st.selectbox("📂 Select a file to review:", file_names) if file_names else None

# Session state for conversation history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "You are an expert software developer and code reviewer across multiple languages."}
    ]
if "show_suggestions" not in st.session_state:
    st.session_state.show_suggestions = False

# Clear chat button
if st.sidebar.button("🧹 Clear Chat History"):
    st.session_state.messages = [
        {"role": "system", "content": "You are an expert software developer and code reviewer across multiple languages."}
    ]
    st.sidebar.success("Chat history cleared!")

if selected_file:
    current = next(f for f in combined_files if f["name"] == selected_file)
    extension = current["name"].split(".")[-1].lower()
    language_map = {
        "py": "Python",
        "r": "R",
        "js": "JavaScript",
        "java": "Java",
        "cpp": "C++"
    }
    language = language_map.get(extension, "a programming")

    code = sanitize_code(current["content"])

    st.markdown(f"### 💬 What would you like help with? ({language})")

    if st.button("💡 Show Suggestions"):
        st.session_state.show_suggestions = not st.session_state.show_suggestions

    if st.session_state.show_suggestions:
        col1, col2, col3, col4, col5 = st.columns(5)
        if col1.button("Refactor this code"):
            st.session_state["user_prompt"] = "Refactor this code"
        if col2.button("Explain this code"):
            st.session_state["user_prompt"] = "Explain this code"
        if col3.button("Check for security vulnerabilities"):
            st.session_state["user_prompt"] = "Check for security vulnerabilities"
        if col4.button("Summarize what this file does"):
            st.session_state["user_prompt"] = "Summarize what this file does"
        if col5.button("Find overly complex logic"):
            st.session_state["user_prompt"] = "Find overly complex logic"

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
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    st.session_state.messages.append({"role": "user", "content": prompt, "timestamp": timestamp})
                    st.session_state.messages.append({"role": "assistant", "content": reply, "timestamp": timestamp})
                    st.success("✅ Response received!")
                except Exception as e:
                    st.error(f"Error: {e}")
        else:
            st.warning("Please enter a prompt to run.")

    st.markdown("---")
    st.markdown("### 💬 Conversation with Code Assistant")
    for msg in st.session_state.messages[1:]:  # Skip system prompt
        if msg["role"] == "user":
            st.markdown(f"<div style='border-radius:8px;padding:10px;margin:10px 0;background:#1e293b;color:#fff;'>🧑‍💻 <b>You</b> <span style='float:right;font-size:smaller;'>{msg['timestamp']}</span><br><br>{msg['content']}</div>", unsafe_allow_html=True)
        elif msg["role"] == "assistant":
            st.markdown(f"<div style='border-radius:8px;padding:10px;margin:10px 0;background:#0f172a;color:#38bdf8;'>🤖 <b>Assistant</b> <span style='float:right;font-size:smaller;'>{msg['timestamp']}</span><br><br>{msg['content']}</div>", unsafe_allow_html=True)
else:
    st.info("⬅️ Upload files or paste a GitHub repo URL to get started.")
