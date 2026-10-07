import subprocess
import datetime
import os
import base64
import requests
import sys
from dotenv import load_dotenv
from ALLOWED_COMMANDS import is_allowed

load_dotenv("/Users/ahmedali/local-ai-helper/.env")

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO = "ahmedali/local-ai-helper"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_PATH = os.path.join(BASE_DIR, "logs", "agent.log")

def log_action(action, detail):
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    with open(LOG_PATH, "a") as f:
        f.write(f"{datetime.datetime.now()} | {action} | {detail}\n")

def run_command(command):
    if not is_allowed(command):
        log_action("REFUSED", command)
        return f"Refused: '{command}' is not on the allowlist."

    print(f"\n⚠️  The agent wants to run: {command}")
    confirm = input("Allow this? [y/N]: ").strip().lower()
    if confirm != "y":
        log_action("DECLINED_BY_USER", command)
        return "Command declined by user."

    result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
    log_action("EXECUTED", command)
    return result.stdout + result.stderr

def github_get_file(path):
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{path}"
    headers = {"Authorization": f"Bearer {GITHUB_TOKEN}"}
    response = requests.get(url, headers=headers)
    log_action("GITHUB_READ", path)
    if response.status_code != 200:
        return f"Error: {response.status_code} — {response.json().get('message')}"
    content = response.json()["content"]
    return base64.b64decode(content).decode("utf-8")

def read_file(path):
    try:
        full_path = os.path.join(os.path.dirname(BASE_DIR), path)
        with open(full_path, "r") as f:
            content = f.read()
        log_action("LOCAL_READ", path)
        return content
    except Exception as e:
        return f"Error reading local file: {str(e)}"

tools = [
    {
        "type": "function",
        "function": {
            "name": "run_command",
            "description": "Run an allowlisted shell command, with user confirmation",
            "parameters": {
                "type": "object",
                "properties": {"command": {"type": "string"}},
                "required": ["command"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "github_get_file",
            "description": "Read a file from the GitHub repo",
            "parameters": {
                "type": "object",
                "properties": {"path": {"type": "string"}},
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read a local file from the project directory",
            "parameters": {
                "type": "object",
                "properties": {"path": {"type": "string"}},
                "required": ["path"]
            }
        }
    },
]

def ask_agent(question):
    messages = [
        {
            "role": "system", 
            "content": (
                "You are a tool-using AI assistant. You have access to tools: run_command, github_get_file, read_file. "
                "CRITICAL: When the user asks to run a command, you MUST output a tool call for run_command. "
                "Never reply with plain text when a tool is requested."
            )
        },
        {"role": "user", "content": question}
    ]
    response = requests.post("http://localhost:11434/api/chat", json={
        "model": "qwen2.5:7b", "messages": messages, "tools": tools, "stream": False
    }).json()
    
    if "message" not in response:
        return f"Error communicating with Ollama: {response}"
        
    msg = response["message"]

    if not msg.get("tool_calls"):
        print(f"\n[DEBUG] Model returned text instead of a tool call: {msg.get('content')}")

    if msg.get("tool_calls"):
        messages.append(msg)
        for call in msg["tool_calls"]:
            name = call["function"]["name"]
            args = call["function"]["arguments"]
            if name == "run_command":
                result = run_command(args["command"])
            elif name == "github_get_file":
                result = github_get_file(args["path"])
            elif name == "read_file":
                result = read_file(args["path"])
            else:
                result = f"Error: Unknown tool {name}"
            messages.append({"role": "tool", "content": result})
            
        final = requests.post("http://localhost:11434/api/chat", json={
            "model": "qwen2.5:7b", "messages": messages, "stream": False
        }).json()
        return final["message"]["content"]
    return msg["content"]

if __name__ == "__main__":
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
    else:
        query = "Run git status"
    print(ask_agent(query))