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

## Step 3: Tool/Function Calling

### 1. Python Virtual Environment (venv)
* **What I did:** Created an isolated Python environment inside `tools/venv/` and installed `requests` into it, rather than into my Mac's system Python.
* **Why I did it:** Keeps this project's dependencies separate from anything else on my Mac — same isolation idea as Docker, just one level lighter, for a single script instead of a whole service.
* **My Understanding:** A venv is a private folder of installed packages; activating it (`source venv/bin/activate`) tells my terminal "use this Python and these packages, not the system ones" until I deactivate it.

### 2. Tool/Function Calling (the raw mechanism)
* **What I did:** Sent a raw `curl` request to Ollama's `/api/chat` endpoint with a `tools` field describing a `multiply` function, and inspected the `tool_calls` section of the response.
* **Why I did it:** To see, before writing any code, exactly what a model "asking to call a tool" actually looks like at the API level — a JSON object, not magic.
* **My Understanding:** The model never runs the function itself — it just returns a structured request ("call `multiply` with `a=15, b=7`"). My own code is responsible for actually running it and sending the result back.

### 3. The Tool-Calling Loop
* **What I did:** Wrote `read_file_agent.py`, which sends a question + tool schema to Ollama, catches a `read_file` tool call in the response, actually reads the file, and sends the result back for a final answer.
* **Why I did it:** This is the exact loop that turns a chatbot into something that can take real actions — send message + tools → model requests a call → my code runs it → result goes back → model gives a final answer.
* **My Understanding:** This same five-step loop is what every future tool (terminal commands, GitHub access) will be built on — only the tool itself changes, not the mechanism.

### 4. Sandboxing / Scoping a Tool
* **What I did:** Restricted `read_file` so it can only read files inside my project folder, using `os.path.abspath` plus a `startswith` check against `PROJECT_ROOT`.
* **Why I did it:** The model's own judgment isn't the safety mechanism — my code enforcing a hard boundary is. This tool should never be able to read anything outside the project, no matter what's asked of it.
* **My Understanding:** Real safety here isn't about the model being polite or careful — it's about the tool's code physically refusing to do anything outside its allowed scope.

### 5. Adversarial Testing (Trying to Break My Own Sandbox)
* **What I did:** Deliberately asked the agent to read a path like `../../../../etc/passwd`, to try to escape the project folder.
* **Why I did it:** Building a safety boundary means nothing if I never actually test it — I wanted proof, not an assumption.
* **My Understanding:** The `startswith` check correctly blocked the attempt and returned an error instead of the real file contents — confirming the sandbox works as intended, not just in theory.

### 6. Read-Only First, Deliberately
* **What I did:** Kept this tool strictly read-only — no write, delete, or execute capability anywhere in the script.
* **Why I did it:** Before granting any tool broader permissions (terminal access, GitHub write access), I wanted to understand and prove out the mechanism somewhere with zero risk if something went wrong.
* **My Understanding:** Broader, riskier tools (Step 5) should be built on top of a confirmation/safety layer, not added ad hoc — expanding tool permissions before that layer exists would mean skipping the exact safeguard that makes it safe to use in the first place.
## Step 4: RAG (Embeddings + Vector Database)
 
### 1. Embeddings
* **What I did:** Pulled a dedicated embedding model (`nomic-embed-text`) separate from my chat model, and used it to turn text into vectors (lists of numbers representing meaning).
* **Why I did it:** Embeddings are what let a computer compare two pieces of text by *meaning* rather than exact word matching — the foundation everything else in this step is built on.
* **My Understanding:** An embedding model is a different kind of model from a chat model — one turns text into numbers for comparison, the other generates text as a response. They work together but aren't interchangeable.
### 2. Chunking & Ingestion
* **What I did:** Wrote `ingest.py`, which scans my `docs/` folder, splits each file into chunks, embeds each chunk, and stores it in a local ChromaDB vector database along with which file it came from.
* **Why I did it:** Embedding a whole file at once loses precision — smaller chunks let search find the *specific* relevant part of a document, not just the whole thing.
* **My Understanding:** This is a one-time (or run-when-notes-change) step, separate from asking questions — ingestion builds the searchable database; it doesn't answer anything itself.
### 3. Vector Database & Similarity Search
* **What I did:** Used ChromaDB as a local, file-based vector database — no separate Docker container needed, just a Python library writing to disk.
* **Why I did it:** A vector database is built specifically to store embeddings and quickly find the ones most similar to a new query — regular databases search by exact match, this searches by closeness in meaning.
* **My Understanding:** When I ask a question, it also gets embedded, and ChromaDB finds the stored chunks whose embeddings are numerically closest to it — that's the actual "search by meaning" mechanism.
### 4. Retrieval-Augmented Generation (RAG), End to End
* **What I did:** Wrote `ask.py`, which embeds my question, retrieves the most relevant chunks from ChromaDB, and sends both the question and those chunks to Qwen 2.5 for a final answer.
* **Why I did it:** This is the actual RAG pattern — retrieve relevant context first, then hand it to the model, instead of relying purely on the model's general training.
* **My Understanding:** Confirmed this is genuinely working, not just running without errors — asking "What issues did I hit setting up MongoDB?" correctly returned the real kernel 6.19 incompatibility and the `mongo:7` fix, specific details that only exist in my own journal, not in the model's general knowledge.
# Step 5: Agents (Terminal + GitHub, Safely)
 
### 1. Command Allowlisting
* **What I did:** Built `ALLOWED_COMMANDS.py` with a fixed list of safe command prefixes (`git status`, `git log`, `ls`, `pytest`, etc.), and an `is_allowed()` check that runs before anything else.
* **Why I did it:** The agent should never be able to run "whatever it decides" — only a small, deliberately reviewed set of commands should ever be possible, with everything else refused automatically.
* **My Understanding:** Verified directly that `is_allowed("rm -rf /")` returns `False` — confirming destructive commands are rejected by the allowlist itself, before any confirmation step is even reached.
### 2. Human-in-the-Loop Confirmation
* **What I did:** Added a real confirmation prompt (`input("Allow this? [y/N]: ")`) inside `run_command`, so nothing executes without me explicitly typing `y`.
* **Why I did it:** Even for allowlisted commands, I wanted a genuine pause-and-ask step before anything actually runs — not just trusting the model's judgment.
* **My Understanding:** Tested both paths directly — an off-list command (`rm -rf /`) was refused instantly with no prompt at all, while an allowlisted command (`git status`) genuinely paused and waited for my input before running.
### 3. Two-Layer Defense
* **What I did:** Confirmed the allowlist check happens *before* the confirmation prompt, not after.
* **Why it matters:** Even if I'd accidentally typed `y` to something dangerous, it would never have reached that point — the allowlist is checked first and blocks it completely, independent of my own judgment in the moment.
* **My Understanding:** This is a deliberate two-layer design: the allowlist is a hard, code-enforced wall (like Step 3's sandboxing), and confirmation is a second, independent layer on top — not a replacement for it.
### 4. GitHub Personal Access Token (Least Privilege)
* **What I did:** Created a fine-grained GitHub PAT scoped to exactly one repository, with "Contents: Read-only" permission and nothing else.
* **Why I did it:** A token scoped this narrowly means that even if it leaked, it could only read file contents from one specific repo — nothing else on my GitHub account would be reachable with it.
* **My Understanding:** Verified this directly — hitting a broader GitHub API endpoint (`/user`) with this token correctly failed, confirming the token genuinely can't do anything beyond its narrow scope, not just that I assumed it couldn't.
### 5. Authenticated API Calls
* **What I did:** Built `github_get_file`, which sends `Authorization: Bearer {GITHUB_TOKEN}` as a header to GitHub's REST API, and decodes the base64-encoded file content it returns.
* **Why I did it:** This header is what proves to GitHub's API that a request is genuinely authenticated as me, with exactly the permissions I granted the token.
* **My Understanding:** Confirmed this worked end-to-end by fetching a real file (`docker/docker-compose.yml`) directly from GitHub, not from my local disk — proving the API call itself was live and correctly authenticated.
### 6. Audit Logging
* **What I did:** Logged every single action — refused, declined, and executed — to `logs/agent.log`, with a timestamp, regardless of outcome.
* **Why I did it:** If anything unexpected ever happens, I need a complete, real record of exactly what the agent attempted and when — not just the successful runs.
* **My Understanding:** Checked the log file directly and confirmed it contains a full trail of every test I ran, which is the actual accountability mechanism behind this whole step, not just a nice-to-have.
### 7. The Full Agent Loop
* **What I did:** Combined `read_file` (Step 3), `run_command`, and `github_get_file` into one tool-calling loop, so a single question can trigger whichever tool is actually needed.
* **Why it matters:** This is genuinely the core of what I originally wanted — an assistant that can look at my code, run things (with my permission), and pull from GitHub — built safely, piece by piece, instead of granting broad access all at once.
