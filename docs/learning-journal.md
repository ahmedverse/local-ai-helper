# My Local AI Helper & Ticket Automation Journey

## Step 1: Foundational Environment Setup & Architecture

### 1. Version Control (Git & GitHub)
* **What I did:** Initialized a local repository using `git init` and mapped out a structured directory layout (`docs/`, `docker/`, `src/`, `scripts/`).
* **Why I did it:** To track my project files safely over time, prevent accidental data loss, and allow me to experiment without breaking things permanently.
* **My Understanding:** Git acts as a timeline tracker for my code, letting me save checkpoints (commits) as I build each layer of the AI system.

### 2. Isolation & Virtualization (Docker Desktop)
* **What I did:** Installed Docker Desktop for Mac and verified the daemon is active using `docker info`.
* **Why I did it:** Instead of installing databases and web servers directly onto my macOS system files—which can clutter my computer or cause software dependency conflicts—Docker lets me run applications safely inside isolated "containers."
* **My Understanding:** A container is like an independent virtual box that contains everything an app needs to run. It ensures that whatever runs on my Mac will run identically anywhere else.

### 3. Local AI Engine (Ollama)
* **What I did:** Installed Ollama and ran a test command (`ollama run qwen2.5:7b`) to pull and test an open-weights model locally.
* **Why I did it:** To power our AI helper entirely offline. Using Ollama keeps all of my data completely private on my MacBook's hardware and avoids cloud API subscription costs.
* **My Understanding:** Ollama acts as a local background server (daemon) that exposes an OpenAI-compatible API on my machine (`http://localhost:11434`), allowing other local applications to talk to the AI model seamlessly.

### 4. Architectural Vision
* **What I designed:** A local, containerized service loop where my browser talks to a user interface container (LibreChat), which queries Ollama for text generation and local databases for RAG memory—all bounded entirely within my MacBook.