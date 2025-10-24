# RAG Chatbot with Gemini AI

A production-ready Retrieval-Augmented Generation (RAG) chatbot using Google Gemini AI, ChromaDB, and Sentence Transformers for embeddings.

## 🌐 Live Demo

- **Frontend:** [https://rag-chatbot-frontend-bjj8.onrender.com](https://rag-chatbot-frontend-bjj8.onrender.com)
- **Backend API:** [https://rag-chatbot-backend-iwdg.onrender.com](https://rag-chatbot-backend-iwdg.onrender.com)
- **API Docs:** [https://rag-chatbot-backend-iwdg.onrender.com/docs](https://rag-chatbot-backend-iwdg.onrender.com/docs)

## 🚀 Features

- **Google Gemini AI Integration** - Uses gemini-1.5-flash for accurate responses
- **Free TF-IDF Embeddings** - No costly OpenAI API dependencies 
- **ChromaDB Vector Store** - Persistent document storage and retrieval
- **Multi-format Support** - Upload PDF, DOCX, and HTML documents
- **Chat History** - Maintains conversation context across sessions
- **FastAPI Backend** - RESTful API with automatic documentation
- **Real-time Logging** - Comprehensive activity tracking

## 📁 Project Structure

```
rag-chatbot/
├── main.py              # FastAPI application entry point
├── langchain_utils.py   # RAG chain and LLM configuration
├── chroma_utils.py      # Vector store and document processing
├── db_utils.py          # SQLite database operations
├── pydantic_models.py   # API request/response models
├── requirements.txt     # Python dependencies
├── .env                 # Environment variables (Google API key)
├── app.log             # Application logs
├── rag_app.db          # SQLite database
├── chroma_db/          # ChromaDB persistent storage
└── uploads/            # Uploaded documents storage
```

## 🛠️ Setup & Installation

1. **Clone and navigate to the project:**
   ```bash
   cd rag-chatbot
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   - Get a Google API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Update `.env` file with your API key:
   ```
   GOOGLE_API_KEY=your_google_api_key_here
   ```

4. **Start the server:**
   ```bash
   python -m uvicorn main:app --reload --port 8000
   ```

## 🎯 API Endpoints

- **GET /** - Welcome message
- **POST /chat** - Send chat messages to the RAG system
- **POST /upload-doc** - Upload documents (PDF, DOCX, HTML)
- **POST /delete-doc** - Delete documents by file ID
- **GET /list-docs** - List all uploaded documents
- **GET /docs** - Interactive API documentation

## 💬 Usage Examples

### Upload a Document
```bash
curl -X POST "http://localhost:8000/upload-doc" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@document.pdf"
```

### Chat with Documents
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is this document about?",
    "model": "gemini-1.5-flash"
  }'
```

## 🔧 Configuration

- **Embedding Model:** TF-IDF (free, offline)
- **LLM Model:** Google Gemini 2.5 Flash
- **Vector Store:** ChromaDB with persistent storage
- **Chunk Size:** 1000 characters with 200 overlap
- **Max Retrieval:** 2 most relevant documents per query

## 📊 Performance Metrics

Based on testing with resume documents:
- **Query Processing:** ~2-3 seconds average
- **Document Indexing:** ~5-10 seconds per document
- **Accuracy:** High contextual relevance with specific details
- **Memory Usage:** Optimized for local deployment

## 🔒 Security & Privacy

- All data stored locally (no external dependencies for embeddings)
- Google API key required only for LLM inference
- SQLite database for chat history
- No sensitive data sent to external services

## 📝 Logging

All activities are logged to `app.log` including:
- User queries and AI responses
- Document upload/deletion events
- System errors and warnings
- Performance metrics


## 🔧 Troubleshooting

1. **Server won't start:** Check if Google API key is set in `.env`
2. **Upload fails:** Ensure file format is PDF, DOCX, or HTML
3. **Poor responses:** Upload more relevant documents
4. **Memory issues:** Reduce chunk size in `chroma_utils.py`



---

**Built with:** FastAPI, LangChain, ChromaDB, Google Gemini AI, and ❤️
