from mcp.server.fastmcp import FastMCP
from ALLOWED_COMMANDS import is_allowed
import subprocess
import datetime
import os
import base64
import requests
from dotenv import load_dotenv

# Automatically determine the project root (prioritizing the mounted /workspace repository)
DEFAULT_BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if os.path.exists("/workspace/.git"):
    PROJECT_ROOT = os.getenv("PROJECT_BASE_DIR", "/workspace")
else:
    PROJECT_ROOT = os.getenv("PROJECT_BASE_DIR", DEFAULT_BASE if os.path.exists(os.path.join(DEFAULT_BASE, ".git")) else "/app")

# Load .env dynamically from the project root
load_dotenv(os.path.join(PROJECT_ROOT, ".env"))

mcp = FastMCP("local-ai-helper-tools")

LOG_PATH = os.path.join(PROJECT_ROOT, "tools", "logs", "agent.log")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO = os.getenv("GITHUB_REPO", "yourusername/local-ai-helper")  # Fallback or env-driven

# Holds one pending command at a time, waiting for approval
_pending_command = {"command": None}

def log_action(action, detail):
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    with open(LOG_PATH, "a") as f:
        f.write(f"{datetime.datetime.now()} | {action} | {detail}\n")

@mcp.tool()
def read_file(path: str) -> str:
    """Read a file inside the local-ai-helper project folder."""
    full_path = os.path.abspath(os.path.join(PROJECT_ROOT, path))
    if not full_path.startswith(PROJECT_ROOT):
        return "Error: access outside project folder is not allowed."
    if not os.path.isfile(full_path):
        return f"Error: {path} not found."
    with open(full_path) as f:
        return f.read()

@mcp.tool()
def github_get_file(path: str) -> str:
    """Read a file from the GitHub repo (read-only)."""
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{path}"
    headers = {"Authorization": f"Bearer {GITHUB_TOKEN}"}
    response = requests.get(url, headers=headers)
    log_action("GITHUB_READ", path)
    if response.status_code != 200:
        return f"Error: {response.status_code} — {response.json().get('message', 'Unknown error')}"
    content = response.json()["content"]
    return base64.b64decode(content).decode("utf-8")

@mcp.tool()
def propose_command(command: str) -> str:
    """Propose a shell command to run. Does NOT execute it — requires approve_command() next."""
    if not is_allowed(command):
        log_action("REFUSED", command)
        return f"Refused: '{command}' is not on the allowlist. Nothing was proposed."
    _pending_command["command"] = command
    log_action("PROPOSED", command)
    return f"Proposed command: '{command}'. Call approve_command() to run it, or do nothing to cancel."

@mcp.tool()
def approve_command() -> str:
    """Actually run the most recently proposed command."""
    command = _pending_command["command"]
    if not command:
        return "No command is currently pending approval."
    
    # Executing with cwd=PROJECT_ROOT ensures git commands target your repository directory
    result = subprocess.run(
        command, 
        shell=True, 
        capture_output=True, 
        text=True, 
        timeout=30, 
        cwd=PROJECT_ROOT
    )
    
    log_action("EXECUTED", command)
    _pending_command["command"] = None
    return result.stdout + result.stderr

if __name__ == "__main__":
    mcp.run()