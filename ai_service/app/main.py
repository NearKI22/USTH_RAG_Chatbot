import os
import shutil
import warnings
from fastapi import FastAPI, UploadFile, File  # Handle file uploads from Spring Boot
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel                 # Define JSON data format

# Turn off FutureWarning of SDK
warnings.filterwarnings("ignore", category=FutureWarning)

# Import LangChain RAG libraries
from langchain_chroma import Chroma
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

# Configuration
from app.config import GEMINI_API_KEY, GEMINI_MODEL, GEMINI_EMBEDDING_MODEL, DATA_FOLDER, CHROMA_DB_PATH

# Libraries for DOCX processing and OCR
import zipfile
import xml.etree.ElementTree as ET
import google.generativeai as genai
from langchain_core.documents import Document

# Set environment variables for API keys
os.environ["GOOGLE_API_KEY"] = GEMINI_API_KEY
genai.configure(api_key=GEMINI_API_KEY)

# Function to extract text from DOCX files
# Using built-in zipfile and xml.etree instead of external dependencies
def get_docx_text(path):
    """
    Extracts text from docx without needing python-docx library
    """
    WORD_NAMESPACE = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
    PARA = WORD_NAMESPACE + 'p'
    TEXT = WORD_NAMESPACE + 't'
    
    with zipfile.ZipFile(path) as docx:
        tree = ET.parse(docx.open('word/document.xml'))
        root = tree.getroot()
        paragraphs = []
        for paragraph in root.iter(PARA):
            texts = [node.text for node in paragraph.iter(TEXT) if node.text]
            if texts:
                paragraphs.append(''.join(texts))
        return '\n\n'.join(paragraphs)

# Initialize LangChain RAG Pipeline
embeddings_model = GoogleGenerativeAIEmbeddings(model=GEMINI_EMBEDDING_MODEL)
# Store Vector DB on disk
db = Chroma(persist_directory=CHROMA_DB_PATH, embedding_function=embeddings_model)


llm = ChatGoogleGenerativeAI(model=GEMINI_MODEL, temperature=0.2)

# Strict Context Guardrails
# Use PromptTemplate to lock context, prevent hallucination, and block out-of-scope queries
prompt_template = """
Bạn là chuyên gia tư vấn tuyển sinh đại học thông minh, thân thiện và lịch sự.
Nhiệm vụ của bạn là đọc các dữ liệu được cung cấp trong phần Context để trả lời câu hỏi của người dùng.
Luật lệ bắt buộc (Strict Rules):
1. NẾU NGƯỜI DÙNG CHỈ CHÀO HỎI, CẢM ƠN HOẶC TẠM BIỆT: Hãy đáp lại lịch sự tương ứng (ví dụ: không có gì, chào tạm biệt và chúc may mắn...).
2. NẾU CÂU HỎI KHÔNG LIÊN QUAN ĐẾN GIÁO DỤC/TUYỂN SINH: BẠN PHẢI TỪ CHỐI bằng câu: "Xin lỗi, tôi là trợ lý AI tư vấn tuyển sinh nên chỉ có thể giải đáp các thông tin liên quan đến giáo dục."
3. NẾU CONTEXT KHÔNG CÓ THÔNG TIN (Ví dụ: hỏi về trường ngoài dữ liệu, hoặc yêu cầu gợi ý trường khác): Tuyệt đối không lấy dữ liệu của trường này đắp vào trường kia. Hãy khéo léo nói: "Hiện tại tài liệu của tôi chưa cập nhật thông tin chi tiết về trường/ngành này. Tuy nhiên, theo kiến thức chung..." và sau đó thoải mái dùng kiến thức nền của bạn để tư vấn, gợi ý trường ngoài cho họ.
4. QUAN TRỌNG NHẤT VỀ NGUỒN: Nếu bạn KHÔNG CẦN dùng dữ liệu trong Context để trả lời (ví dụ: chào hỏi, cảm ơn, từ chối, hoặc tư vấn trường ngoài bằng kiến thức nền ở luật 3), bạn BẮT BUỘC phải thêm từ khóa "[NO_SOURCE]" vào cuối câu trả lời của bạn. Ngược lại, nếu bạn có lấy bất kỳ thông tin nào từ Context, tuyệt đối KHÔNG được thêm từ khóa này.
5. GỢI Ý CÂU HỎI: BẮT BUỘC ở cuối cùng của câu trả lời, hãy suy luận và cung cấp đúng 3 câu hỏi ngắn (mỗi câu dưới 15 chữ) mà người dùng có thể muốn hỏi tiếp theo. Phải đặt 3 câu hỏi này trong đúng định dạng sau: [GOI_Y: Câu 1 | Câu 2 | Câu 3]. Tuyệt đối không viết sai định dạng này.

Context: {context}

Question: {question}

Answer:"""

PROMPT = PromptTemplate(
    template=prompt_template, input_variables=["context", "question"]
)

# Integrate the prompt and enable source documents return
qa_chain = RetrievalQA.from_chain_type(
    llm=llm, 
    chain_type="stuff",
    retriever=db.as_retriever(search_kwargs={"k": 6}),
    return_source_documents=True,
    chain_type_kwargs={"prompt": PROMPT}
)
print("Successfully connected to AI LangChain API")

# Initialize FastAPI server
app = FastAPI(
    title="RAG Chatbot API",
    description="API này đóng vai trò là Backend AI Engine, nhận câu hỏi từ Java Spring Boot và trả về câu trả lời bằng LangChain.",
    version="1.0.0"
)

# Serve static document files so users can click source links
app.mount("/documents", StaticFiles(directory=DATA_FOLDER), name="documents")

# Define data schemas
# FastAPI uses these schemas to parse JSON payloads from Java

class ChatRequest(BaseModel):
    query: str
    
class ChatResponse(BaseModel):
    answer: str
    status: str = "success"


# Endpoint for handling chat questions (POST /ask)

@app.post("/ask", response_model=ChatResponse)
async def ask_question(request: ChatRequest):
    """
    Receives questions from the Java backend, runs the LangChain RAG pipeline
    to search for vectors in ChromaDB, and calls Gemini for the answer.
    """
    
    cau_hoi = request.query
    
    # Run RAG Pipeline
    print(f"\n[+] Receive Question: {cau_hoi}")
    
    # Call the QA chain to find relevant vectors and generate an answer
    response = qa_chain.invoke(cau_hoi)
    cau_tra_loi = response['result']
    
    # Source Citations logic
    if "[NO_SOURCE]" in cau_tra_loi:
        # If AI marks as not using source (greeting, refusal), remove the flag and do not print the source.
        cau_tra_loi = cau_tra_loi.replace("[NO_SOURCE]", "").strip()
    else:
        # Get metadata of vector files used to generate answers
        source_docs = response.get('source_documents', [])
        if source_docs:
            sources = set()
            for doc in source_docs:
                if 'source' in doc.metadata:
                    # Take only the file name, remove the long directory path
                    filename = os.path.basename(doc.metadata['source'])
                    sources.add(filename)
            
            if sources:
                # Format as markdown links: [filename](http://localhost:8000/documents/filename)
                source_links = [f"[{src}](http://localhost:8000/documents/{src})" for src in sources]
                source_text = ", ".join(source_links)
                # Append the citation line directly to the end of the response to React
                cau_tra_loi += f"\n\n*(Nguồn tài liệu: {source_text})*"
            
    print(f" Answer: {cau_tra_loi}")
    
    return ChatResponse(answer=cau_tra_loi)


# Endpoint for uploading and indexing new documents (POST /index)

@app.post("/index")
async def index_document(file: UploadFile = File(...)):
    """
    Allows the Admin portal (Java) to upload PDF, DOCX, or TXT files.
    Extracts text, splits into chunks, embeds vectors, and saves to ChromaDB.
    Includes OCR fallback using Gemini for scanned PDFs.
    """
  
    if not os.path.exists(DATA_FOLDER):
        os.makedirs(DATA_FOLDER)
        
    file_location = os.path.join(DATA_FOLDER, file.filename)
    
    with open(file_location, "wb+") as file_object:
        shutil.copyfileobj(file.file, file_object)
    print(f"Processing file: {file.filename}")
    
    from langchain_community.document_loaders import PyPDFLoader, TextLoader
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    
    docs = []
    
    # Load document based on file extension
    if file.filename.endswith('.pdf'):
        # Use PyPDFLoader to extract text
        loader = PyPDFLoader(file_location)
        docs = loader.load()
        
        # Check if the PDF is a scanned image (contains very little text)
        # If character count < 50, assume it's a scanned PDF
        total_text_length = sum(len(doc.page_content) for doc in docs)
        
        if total_text_length < 50:
            print(f"[*] Warning: File {file.filename} contains no text (likely a scanned PDF).")
            print("[*] Starting OCR process via Google Gemini API...")
            try:
                # Upload file to Gemini for text extraction (OCR)
                uploaded_file = genai.upload_file(path=file_location, mime_type="application/pdf")
                model = genai.GenerativeModel(GEMINI_MODEL)
                response = model.generate_content(
                    [uploaded_file, "Hãy đọc toàn bộ văn bản trong tài liệu PDF này và trả về dưới dạng Text. Chỉ trả về nội dung văn bản, không thêm bình luận nào khác."]
                )
                
                # Create a Langchain Document object with the OCR output
                docs = [Document(page_content=response.text, metadata={"source": file_location})]
                print("[*] OCR completed successfully!")
            except Exception as e:
                print(f"[!] Error calling Gemini OCR: {str(e)}")
                # Return an error response to the user
                return {"status": "error", "message": f"OCR Error: {str(e)}"}
                
    elif file.filename.endswith('.docx'):
        # Call custom DOCX parser to avoid additional dependencies
        print(f"[*] Extracting text from Word file (.docx)...")
        try:
            text_content = get_docx_text(file_location)
            docs = [Document(page_content=text_content, metadata={"source": file_location})]
        except Exception as e:
            print(f"[!] Error parsing DOCX file: {str(e)}")
            return {"status": "error", "message": f"Error reading DOCX: {str(e)}"}
            
    else:
        # Default to TextLoader for other file types (.txt)
        loader = TextLoader(file_location, encoding='utf-8')
        docs = loader.load()
    
    # Text Chunking
    # Split text into smaller chunks to provide better context for the Chatbot
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    chunks = text_splitter.split_documents(docs)
    
    # Embed into ChromaDB instantly
    # Embed vectors and save directly into ChromaDB
    db.add_documents(chunks)
    print(f" Successfully embedded {len(chunks)} chunks into ChromaDB!")
        
    return {
        "status": "success",
        "message": f"File {file.filename} has been uploaded and vectorized successfully!",
        "filename": file.filename
    }

# uvicorn app.main:app
#uvicorn app.main:app --reload --port 8000
# http://127.0.0.1:8000/docs