# Configuration File
# Stores API keys, model parameters, and database paths.

GEMINI_API_KEY = "YOUR_GEMINI_API_KEY_HERE"

# Model used for generating text responses
GEMINI_MODEL = "gemini-3.1-flash-lite"
# Model used for generating text embeddings (text -> vector)
GEMINI_EMBEDDING_MODEL = "models/gemini-embedding-001"

# Directory path to store ChromaDB (Vector Database)
CHROMA_DB_PATH = "./chroma_db"

# Default folder path containing your data files (PDF, TXT)
DATA_FOLDER = "./data/"
