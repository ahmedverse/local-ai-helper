import os
import chromadb
from chromadb.utils.embedding_functions.ollama_embedding_function import OllamaEmbeddingFunction

# Setup paths (Flexible: uses current folder by default, or can be overridden anywhere via PROJECT_BASE_DIR)
DEFAULT_BASE = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.getenv("PROJECT_BASE_DIR", DEFAULT_BASE)
DOCS_DIR = os.path.join(BASE_DIR, "docs")
DB_DIR = os.path.join(BASE_DIR, "chroma_db")

# Initialize ChromaDB persistent client
client = chromadb.PersistentClient(path=DB_DIR)

# Use Chroma's native Ollama embedding function
embedding_fn = OllamaEmbeddingFunction(
    url="http://localhost:11434",
    model_name="nomic-embed-text"
)

# Get or create our collection
collection_name = "local_notes"
collection = client.get_or_create_collection(
    name=collection_name, 
    embedding_function=embedding_fn
)

def ingest_docs():
    print("📂 Scanning docs folder...")
    if not os.path.exists(DOCS_DIR):
        os.makedirs(DOCS_DIR)
        print(f"Created {DOCS_DIR}. Please add some markdown files there!")
        return

    # Check if docs folder is empty
    files = [f for f in os.listdir(DOCS_DIR) if f.endswith(".md")]
    if not files:
        print(f"⚠️ No markdown files found in {DOCS_DIR}. Add a .md file first!")
        return

    # Read all markdown files in docs/
    for filename in files:
        file_path = os.path.join(DOCS_DIR, filename)
        with open(file_path, "r") as f:
            content = f.read()
            
        collection.upsert(
            documents=[content],
            metadatas=[{"source": filename}],
            ids=[filename]
        )
        print(f"✅ Ingested and embedded: {filename}")

    print("\n🎉 Ingestion complete! Your notes are now vectorized in ChromaDB.")

if __name__ == "__main__":
    ingest_docs()