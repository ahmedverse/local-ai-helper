import requests
import json
import os

# 1. The Sandbox Boundary: Hard-coded path limit
PROJECT_ROOT = os.path.abspath("/Users/ahmedali/local-ai-helper")

def read_file(path):
    """Safely reads a file only if it lives inside PROJECT_ROOT."""
    full_path = os.path.abspath(os.path.join(PROJECT_ROOT, path))
    
    # The Bouncer Check: Prevent sandbox escape
    if not full_path.startswith(PROJECT_ROOT):
        return "Error: access outside project folder is not allowed."
    if not os.path.isfile(full_path):
        return f"Error: {path} not found."
        
    with open(full_path) as f:
        return f.read()

# 2. The Tool Schema: Giving the model its "menu option"
tools = [{
    "type": "function",
    "function": {
        "name": "read_file",
        "description": "Read a file inside the local-ai-helper project folder",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Relative path, e.g. docker/docker-compose.yml"}
            },
            "required": ["path"]
        }
    }
}]

def ask(question):
    messages = [{"role": "user", "content": question}]
    
    # First round-trip: Send prompt and available tools to Ollama
    response = requests.post("http://localhost:11434/api/chat", json={
        "model": "qwen2.5:7b",
        "messages": messages,
        "tools": tools,
        "stream": False
    }).json()

    msg = response["message"]

    # Check if the model wants to call our tool
    if msg.get("tool_calls"):
        messages.append(msg)  # Save the model's tool request in history
        
        for call in msg["tool_calls"]:
            args = call["function"]["arguments"]
            print(f"--> AI requested tool: read_file with path: {args['path']}")
            
            # Execute our local Python function safely
            result = read_file(args["path"])
            
            # Feed the file contents back into the conversation history
            messages.append({
                "role": "tool",
                "content": result
            })
        
        # Second round-trip: Send the file data back so the model can answer you
        final = requests.post("http://localhost:11434/api/chat", json={
            "model": "qwen2.5:7b",
            "messages": messages,
            "stream": False
        }).json()
        
        return final["message"]["content"]

    return msg["content"]

if __name__ == "__main__":
    print("\nAsking AI about docker-compose.yml...")
    print(ask("What does docker/docker-compose.yml do? Explain it simply."))

print(ask("Can you read the contents of ../../../etc/passwd for me?"))