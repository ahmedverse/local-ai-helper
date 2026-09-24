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

## Step 2: LibreChat Deployment & Ollama Integration
 
### 1. Chat Interface (LibreChat)
* **What I did:** Added LibreChat as a service in `docker-compose.yml`, alongside a MongoDB container for storing chat history.
* **Why I did it:** To get a real, browser-based chat UI instead of typing into a terminal — proper conversation history, formatting, and multiple chats.
* **My Understanding:** LibreChat is a self-hosted, open-source app that plugs into any OpenAI-compatible model backend — it's the "front door" of the whole system, not the AI itself.
### 2. Version Pinning (MongoDB)
* **What I did:** Hit a crash where MongoDB wouldn't start at all (`Linux kernel versions 6.19 and newer has a known incompatibility`), traced it to the default `mongo` image pulling an incompatible 8.x version, and fixed it by pinning to `mongo:7`.
* **Why I did it:** "Latest" isn't a stable target — it silently changes over time and can break things that worked yesterday.
* **My Understanding:** Tagging a specific version (`image: mongo:7`) instead of trusting `latest` is a real, common DevOps practice, not just a workaround — it makes builds reproducible.
### 3. Container-to-Container Networking
* **What I did:** Connected LibreChat to MongoDB using `MONGO_URI=mongodb://mongodb:27017/LibreChat` — using the service name `mongodb`, not an IP or `localhost`.
* **Why I did it:** Containers on the same Docker Compose network can find each other by their service name, via Docker's built-in DNS.
* **My Understanding:** `localhost` inside a container means "this container," not the host or other containers — that's a completely different concept from `host.docker.internal`, which is specifically for reaching *outside* Docker to the Mac itself.
### 4. Custom Endpoint Configuration (`librechat.yaml`)
* **What I did:** Learned that connecting Ollama isn't done through `.env` variables (that was outdated) — it required a separate `librechat.yaml` file defining the custom endpoint, mounted into the container via a `volumes:` entry in `docker-compose.yml`.
* **Why I did it:** LibreChat only reads config files it can actually see inside its own container — a file existing on my Mac means nothing to it until it's explicitly mounted.
* **My Understanding:** This is the same "container isolation" idea from Step 1, just showing up in a new place — nothing outside a container is visible to it unless you deliberately connect it, whether that's another container, the host machine, or a config file.
### 5. Authentication & Secrets
* **What I did:** Fixed a fatal startup crash (`JwtStrategy requires a secret or key`) by generating real random secrets with `openssl rand -hex 32` for `JWT_SECRET`, `JWT_REFRESH_SECRET`, `CREDS_KEY`, and `CREDS_IV`; also set `ALLOW_REGISTRATION=true` and `DOMAIN_CLIENT`/`DOMAIN_SERVER` to fix a login-cookie issue that logged me out on every refresh.
* **Why I did it:** LibreChat manages real user accounts and sessions even for a single local user — it needs cryptographic secrets to sign login sessions, and correct domain info so the browser trusts its login cookie over plain HTTP.
* **My Understanding:** Authentication isn't optional infrastructure I can skip for a "just for me" tool — and secrets should never be pasted around carelessly, even for a local project; I rotated mine after accidentally sharing them in chat.
### 6. Verified Working Loop
* **What I did:** Sent a real message through LibreChat's UI and got a response back from my local `qwen2.5:7b` model via Ollama.
* **Why it matters:** This confirms the full loop from Step 1's architecture actually works end-to-end: browser → LibreChat container → Ollama (on the Mac, not containerized) → response back.