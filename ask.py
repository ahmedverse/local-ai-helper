import os
import sys
import chromadb
from chromadb.utils.embedding_functions.ollama_embedding_function import OllamaEmbeddingFunction
import requests

# Setup paths (Flexible: uses current folder by default, or can be overridden anywhere via PROJECT_BASE_DIR)
DEFAULT_BASE = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.getenv("PROJECT_BASE_DIR", DEFAULT_BASE)
DB_DIR = os.path.join(BASE_DIR, "chroma_db")

# Initialize client and embedding function
client = chromadb.PersistentClient(path=DB_DIR)
embedding_fn = OllamaEmbeddingFunction(
    url="http://localhost:11434",
    model_name="nomic-embed-text"
)

# Load existing collection
collection = client.get_or_create_collection(
    name="local_notes",
    embedding_function=embedding_fn
)

def ask_ai(query_text):
    print(f"\n🔍 Searching your notes for: '{query_text}'...")
    
    # Query ChromaDB for the top matching document chunks
    results = collection.query(
        query_texts=[query_text],
        n_results=2
    )
    
    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    
    if not documents:
        print("❌ No relevant notes found in your database.")
        return

    # Combine retrieved text chunks into a single context block
    context = "\n\n".join(documents)
    source_files = set(m.get("source", "unknown") for m in metadatas)
    
    print(f"📄 Found matching context from files: {list(source_files)}")
    
    # Construct the strict prompt for Qwen 2.5
    prompt = f"""You are a strict local AI assistant. Your ONLY source of truth is the provided context below. 

Context:
{context}

Question: {query_text}

Instructions:
- Answer the question using ONLY the facts directly mentioned in the context above.
- If the answer cannot be found in the context, or if the question asks about something outside your ingested notes, you MUST respond with: "I can't give this to you because it's not in your notes."
- Do not use outside knowledge or guess.
"""

    print("🤖 Generating answer with Qwen 2.5...\n")
    response = requests.post("http://localhost:11434/api/generate", json={
        "model": "qwen2.5:7b",
        "prompt": prompt,
        "stream": False
    })
    
    answer = response.json().get("response", "Error generating response from Ollama.")
    print("--- Answer ---")
    print(answer.strip())
    print("--------------")

def interactive_loop():
    print("💡 Entering interactive notes mode. Type 'exit' or 'quit' to stop.\n")
    while True:
        try:
            query = input("Ask notes 💬 ").strip()
            if not query:
                continue
            if query.lower() in ["exit", "quit"]:
                print("Goodbye!")
                break
            ask_ai(query)
            print("\n" + "="*40 + "\n")
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye!")
            break

if __name__ == "__main__":
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        ask_ai(query)
    else:
        interactive_loop()