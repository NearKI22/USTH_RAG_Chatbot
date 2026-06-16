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
Hệ thống được chia thành 3 module (Microservices):
1. **Frontend (ReactJS + Vite):** Giao diện người dùng trực quan, hỗ trợ hiển thị Markdown, đánh giá (Like/Dislike) và quản lý lịch sử trò chuyện.
2. **Backend API Gateway (Java Spring Boot):** Quản lý cơ sở dữ liệu MySQL, lưu trữ lịch sử chat, phản hồi của người dùng và bảo mật JWT.
3. **AI Service (Python FastAPI):** Nền tảng xử lý ngôn ngữ tự nhiên sử dụng LangChain, ChromaDB và Google Gemini.

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
The system is divided into 3 modules (Microservices):
1. **Frontend (ReactJS + Vite):** Intuitive user interface supporting Markdown rendering, user feedback (Like/Dislike), and chat history management.
2. **Backend API Gateway (Java Spring Boot):** Manages the MySQL database, stores chat history, user feedback, and handles JWT security.
3. **AI Service (Python FastAPI):** Natural language processing platform utilizing LangChain, ChromaDB, and Google Gemini.
