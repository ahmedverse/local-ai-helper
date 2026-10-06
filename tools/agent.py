import subprocess
import datetime
import os
import base64
import requests
from dotenv import load_dotenv
from ALLOWED_COMMANDS import is_allowed

# Load environment variables from .env
load_dotenv("/Users/ahmedali/local-ai-helper/.env")

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO = "ahmedverse/local-ai-helper"  # Make sure this matches your GitHub username/repo

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

if __name__ == "__main__":
    print("--- Testing GitHub Read Tool ---")
    print(github_get_file("README.md"))