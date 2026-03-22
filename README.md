# RAG Multi-Document Chatbot

A production-grade Retrieval-Augmented Generation (RAG) chatbot that lets you upload PDF documents, ask questions about them, get answers with source citations, and summarize entire documents.

## Features

- **Upload PDFs** -- drag-and-drop or click to upload PDF documents
- **Ask Questions** -- natural language questions answered from your uploaded documents
- **Source Citations** -- every answer cites the source document and page number
- **Document Summarization** -- generate comprehensive summaries of any uploaded document
- **Chat History** -- maintains conversation context across messages
- **Multi-Document Search** -- queries search across all uploaded documents simultaneously

## Tech Stack

### Backend
- **FastAPI** -- async Python web framework
- **Google Gemini** -- LLM (gemini-1.5-flash) + embeddings (embedding-001)
- **ChromaDB** -- lightweight persistent vector database
- **PyPDF** -- PDF text extraction
- **LangChain Text Splitters** -- intelligent text chunking

### Frontend
- **Next.js 14** (App Router) -- React framework
- **Tailwind CSS** -- utility-first styling
- **Lucide React** -- icons
- **react-dropzone** -- drag-and-drop file uploads
- **react-markdown** -- render markdown in chat responses

## Prerequisites

- **Python 3.11+**
- **Node.js 18+**
- **Google AI API Key** -- get one free at [https://aistudio.google.com/apikey](https://aistudio.google.com/apikey)

## Setup

### 1. Clone and navigate to the project

```bash
cd Chatbot_project
```

### 2. Backend Setup

```bash
cd backend

# Create and activate a virtual environment (recommended)
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your GOOGLE_API_KEY
```

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install
```

### 4. Configure Environment Variables

**Backend** (`backend/.env`):
```
GOOGLE_API_KEY=your_google_api_key_here
CHROMA_PERSIST_DIR=./chroma_db
UPLOAD_DIR=./uploads
```

**Frontend** (`frontend/.env.local`):
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Running the Application

### Start the Backend (Terminal 1)

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000` and interactive docs at `http://localhost:8000/docs`.

### Start the Frontend (Terminal 2)

```bash
cd frontend
npm run dev
```

The UI will be available at `http://localhost:3000`.

## Usage

1. Open `http://localhost:3000` in your browser
2. Upload one or more PDF documents using the sidebar
3. Ask questions in the chat -- the bot will search your documents and respond with citations
4. Click the book icon next to a document to generate a summary
5. Click "New Chat" to start a fresh conversation

## API Endpoints

| Method | Endpoint              | Description                          |
| ------ | --------------------- | ------------------------------------ |
| POST   | `/documents/upload`   | Upload and process a PDF             |
| GET    | `/documents`          | List all uploaded documents          |
| DELETE | `/documents/{doc_id}` | Delete a document and its embeddings |
| POST   | `/chat`               | Ask a question (RAG pipeline)        |
| POST   | `/summarize`          | Summarize a specific document        |
| GET    | `/health`             | Health check                         |

## Architecture

```
User uploads PDF
  -> Extract text (PyPDF)
  -> Chunk text (RecursiveCharacterTextSplitter)
  -> Generate embeddings (Gemini embedding-001)
  -> Store in ChromaDB

User asks question
  -> Embed question (Gemini embedding-001)
  -> Similarity search in ChromaDB (top-5)
  -> Build context from retrieved chunks
  -> Generate answer with Gemini 1.5 Flash
  -> Return answer with source citations
```

## Project Structure

```
Chatbot_project/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI entry point
│   │   ├── config.py            # Settings & env vars
│   │   ├── routes/
│   │   │   ├── chat.py          # Chat endpoint
│   │   │   ├── documents.py     # Document CRUD
│   │   │   └── summarize.py     # Summarization endpoint
│   │   ├── services/
│   │   │   ├── pdf_processor.py # PDF text extraction
│   │   │   ├── chunker.py       # Text splitting
│   │   │   ├── embeddings.py    # Gemini embeddings
│   │   │   ├── vector_store.py  # ChromaDB operations
│   │   │   ├── retriever.py     # Similarity search
│   │   │   └── llm.py           # Gemini LLM wrapper
│   │   └── models/
│   │       └── schemas.py       # Pydantic models
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── app/                 # Next.js pages
│   │   ├── components/          # React components
│   │   └── lib/                 # API client
│   └── package.json
└── README.md
```

## Docker (Optional)

A `docker-compose.yml` is provided for containerized deployment:

```bash
docker-compose up --build
```

This starts both backend and frontend. Access the app at `http://localhost:3000`.
