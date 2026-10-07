import requests
import subprocess

def check_ollama():
    try:
        r = requests.get("http://localhost:11434", timeout=3)
        return r.status_code == 200
    except requests.exceptions.RequestException:
        return False

def check_librechat():
    try:
        r = requests.get("http://localhost:3080", timeout=3)
        return r.status_code == 200
    except requests.exceptions.RequestException:
        return False

def check_containers():
    result = subprocess.run(
        ["docker", "compose", "-f", "/Users/ahmedali/local-ai-helper/docker/docker-compose.yml", "ps"],
        capture_output=True, text=True
    )
    return result.stdout

if __name__ == "__main__":
    print("Checking Local AI Stack Health...\n")
    print("Ollama:   ", "✅ healthy" if check_ollama() else "❌ unreachable")
    print("LibreChat:", "✅ healthy" if check_librechat() else "❌ unreachable")
    print("\nDocker Containers:\n", check_containers())