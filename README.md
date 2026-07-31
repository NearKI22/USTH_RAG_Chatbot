# USTH RAG Chatbot - Trợ lý AI Tư vấn Tuyển sinh Đại học

*[English below](#english-version)*

## 🇻🇳 Phiên bản Tiếng Việt

**USTH RAG Chatbot** là một hệ thống trợ lý ảo thông minh dựa trên kiến trúc **Retrieval-Augmented Generation (RAG)**, được thiết kế để tư vấn tuyển sinh cho 5 trường đại học hàng đầu: USTH, HUST, FTU, NEU và UET.

### 🌟 Tính năng nổi bật
* **Hỏi đáp thông minh (RAG):** Trích xuất thông tin chính xác từ tài liệu tuyển sinh bằng vector search (ChromaDB) và trả lời tự nhiên qua mô hình ngôn ngữ lớn (Google Gemini).
* **Trí nhớ ngắn hạn (Context Window):** Lưu giữ ngữ cảnh của các câu hỏi trước đó, giúp cuộc trò chuyện diễn ra tự nhiên.
* **Gợi ý tự động:** AI tự động phân tích và đưa ra 3 câu hỏi gợi ý tiếp theo phù hợp với ngữ cảnh.
* **Minh bạch thông tin:** Các câu trả lời đều được đính kèm nguồn tài liệu rõ ràng.
* **OCR tích hợp:** Hệ thống tự động nhận diện và trích xuất chữ từ các file PDF dạng quét (scan) thông qua Gemini OCR.

### 🏗️ Kiến trúc hệ thống
Hệ thống được thiết kế theo **kiến trúc phân tán 3 tầng (Three-tier Architecture)**:
1. **Frontend (ReactJS + Vite):** Giao diện người dùng trực quan, hỗ trợ hiển thị Markdown, đánh giá (Like/Dislike) và quản lý lịch sử trò chuyện.
2. **Backend API Gateway (Java Spring Boot):** Quản lý cơ sở dữ liệu MySQL, lưu trữ lịch sử chat, phản hồi của người dùng và bảo mật JWT.
3. **AI Service (Python FastAPI):** Nền tảng xử lý ngôn ngữ tự nhiên sử dụng LangChain, ChromaDB và Google Gemini.

### ⚙️ Hướng dẫn cài đặt và chạy hệ thống

**Yêu cầu môi trường:**
- Node.js (v18+)
- Python (3.10+)
- Java (JDK 17+)
- MySQL (v8.0+)

**Bước 1: Thiết lập cơ sở dữ liệu MySQL**
- Tạo database tên `rag`.
- Chỉnh sửa mật khẩu MySQL trong file `java_backend/src/main/resources/application.properties`.

**Bước 2: Cài đặt và chạy AI Service (Python)**
```bash
cd ai_service
pip install -r requirements.txt
# Cập nhật GEMINI_API_KEY trong app/config.py
uvicorn app.main:app --reload --port 8000
```

> **Lưu ý về dữ liệu:** Folder `ai_service/data/` chứa 27 file `.txt` là dữ liệu tuyển sinh đã được chuẩn hóa. Trước lần chạy đầu tiên, cần nạp dữ liệu vào ChromaDB:
> ```bash
> cd ai_service
> python ingest_clean_data.py
> ```
> Script này sẽ đọc toàn bộ file `.txt` trong `data/`, chia nhỏ thành chunks và tạo vector embeddings lưu vào `chroma_db/`.

**Bước 3: Cài đặt và chạy Backend (Java Spring Boot)**
- Mở thư mục `java_backend` bằng IntelliJ IDEA hoặc Eclipse.
- Cập nhật dependency bằng Maven và chạy file `JavaBackendApplication.java`.
- Server sẽ chạy tại cổng `8080`.

**Bước 4: Cài đặt và chạy Frontend (ReactJS)**
```bash
cd frontend
npm install
npm run dev
```
- Giao diện web sẽ tự động mở tại `http://localhost:5173`.

---

<a name="english-version"></a>
## 🇬🇧 English Version

**USTH RAG Chatbot** is an intelligent virtual assistant system based on the **Retrieval-Augmented Generation (RAG)** architecture, designed to provide university admission consulting for 5 top universities: USTH, HUST, FTU, NEU, and UET.

### 🌟 Key Features
* **Smart Q&A (RAG):** Extracts accurate information from admission documents using vector search (ChromaDB) and provides natural answers via Large Language Models (Google Gemini).
* **Short-term Memory (Context Window):** Retains the context of previous questions, making the conversation natural.
* **Auto Suggestions:** The AI automatically analyzes and provides 3 contextually appropriate follow-up questions.
* **Information Transparency:** Answers are accompanied by clear document source citations.
* **Integrated OCR:** The system automatically recognizes and extracts text from scanned PDF files via Gemini OCR.

### 🏗️ System Architecture
The system is divided into a **Three-tier Architecture**:
1. **Frontend (ReactJS + Vite):** Intuitive user interface supporting Markdown rendering, user feedback (Like/Dislike), and chat history management.
2. **Backend API Gateway (Java Spring Boot):** Manages the MySQL database, stores chat history, user feedback, and handles JWT security.
3. **AI Service (Python FastAPI):** Natural language processing platform utilizing LangChain, ChromaDB, and Google Gemini.

### ⚙️ Installation and Setup

**Requirements:**
- Node.js (v18+)
- Python (3.10+)
- Java (JDK 17+)
- MySQL (v8.0+)

**Step 1: Setup MySQL Database**
- Create a database named `rag`.
- Edit the MySQL password in `java_backend/src/main/resources/application.properties`.

**Step 2: Setup and Run AI Service (Python)**
```bash
cd ai_service
pip install -r requirements.txt
# Update GEMINI_API_KEY in app/config.py
uvicorn app.main:app --reload --port 8000
```

> **Note on data:** The `ai_service/data/` folder contains 27 pre-processed `.txt` files with university admission information. Before the first run, load the data into ChromaDB:
> ```bash
> cd ai_service
> python ingest_clean_data.py
> ```
> This script reads all `.txt` files from `data/`, splits them into chunks, and stores vector embeddings in `chroma_db/`.

**Step 3: Setup and Run Backend (Java Spring Boot)**
- Open the `java_backend` folder in IntelliJ IDEA or Eclipse.
- Update dependencies using Maven and run `JavaBackendApplication.java`.
- The server will run on port `8080`.

**Step 4: Setup and Run Frontend (ReactJS)**
```bash
cd frontend
npm install
npm run dev
```
- The web interface will be available at `http://localhost:5173`.
