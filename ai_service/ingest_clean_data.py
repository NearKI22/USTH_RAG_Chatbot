import os
import shutil
import glob
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
import google.generativeai as genai
from app.config import GEMINI_API_KEY, GEMINI_EMBEDDING_MODEL, CHROMA_DB_PATH

# Setup API key
os.environ["GOOGLE_API_KEY"] = GEMINI_API_KEY
genai.configure(api_key=GEMINI_API_KEY)

AI_SERVICE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_TUYENSINH_DIR = os.path.join(os.path.dirname(AI_SERVICE_DIR), "Data_TuyenSinh")
DATA_FOLDER = os.path.join(AI_SERVICE_DIR, "data")
CHROMA_LANGCHAIN_DB_PATH = os.path.join(AI_SERVICE_DIR, "chroma_langchain_db")

# Cleanup old data
print("[*] Clearing old Vector DB and temporary data...")
for folder in [CHROMA_DB_PATH, CHROMA_LANGCHAIN_DB_PATH, DATA_FOLDER]:
    if os.path.exists(folder):
        shutil.rmtree(folder)
        print(f"  - Deleted {folder}")
    os.makedirs(folder, exist_ok=True)
    print(f"  - Recreated {folder}")

import time


extracted_md_dir = os.path.join(DATA_TUYENSINH_DIR, "extracted_markdown")
files_to_process = []

if os.path.exists(extracted_md_dir):
    for root, _, files in os.walk(extracted_md_dir):
        for file in files:
            if file.lower().endswith('.md'):
                files_to_process.append(os.path.join(root, file))

print(f"[*] Found {len(files_to_process)} Markdown files. Starting data ingestion...")

# Process files
all_docs = []
for file_path in files_to_process:
    filename = os.path.basename(file_path)
    # Rename .md -> .txt so source citations show .txt in the chatbot
    txt_filename = os.path.splitext(filename)[0] + '.txt'
    dest_path = os.path.join(DATA_FOLDER, txt_filename)
    shutil.copy2(file_path, dest_path)

    print(f"  -> Reading: {txt_filename}")
    try:
        loader = TextLoader(dest_path, encoding='utf-8')
        docs = loader.load()
        all_docs.extend(docs)
    except Exception as e:
        print(f"  [!] Error reading file {txt_filename}: {e}")

print(f"[*] Total documents loaded: {len(all_docs)}")

# Text Chunking
print("[*] Splitting text into chunks...")
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
splits = text_splitter.split_documents(all_docs)
print(f"[*] Split into {len(splits)} chunks. Starting ChromaDB embedding...")

# Embedding with Rate Limit Handling
embeddings_model = GoogleGenerativeAIEmbeddings(model=GEMINI_EMBEDDING_MODEL)

batch_size = 50
for i in range(0, len(splits), batch_size):
    batch = splits[i:i+batch_size]
    print(f"[*] Processing batch {i//batch_size + 1} (from chunk {i} to {i+len(batch)})...")
    try:
        Chroma.from_documents(documents=batch, embedding=embeddings_model, persist_directory=CHROMA_DB_PATH)
    except Exception as e:
        print(f"[!] Error in batch {i//batch_size + 1}. Waiting 60s to retry... Error: {e}")
        time.sleep(60)
        Chroma.from_documents(documents=batch, embedding=embeddings_model, persist_directory=CHROMA_DB_PATH)
    
    if i + batch_size < len(splits):
        print("    -> Pausing 10s to avoid API Rate Limits...")
        time.sleep(10)

print("[*] DONE! All data successfully ingested into the system.")
