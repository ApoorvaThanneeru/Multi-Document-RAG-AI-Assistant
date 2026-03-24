# Multi-Document RAG AI Assistant

AI-powered assistant for context-aware question answering and content generation across multiple documents using Retrieval-Augmented Generation (RAG).

---

## 🚀 Features

- Upload and query multiple PDF documents  
- Context-aware question answering using RAG  
- Source citations with document and page reference  
- Document summarization  
- Multi-turn conversation with chat history  

---

## 🖼️ Demo

<img width="1898" height="855" alt="image" src="https://github.com/user-attachments/assets/313ce12a-f0c4-48e7-97f5-d82ef5cf5571" />


- Chat interface  
- Document upload  
- Sample Q&A with citations  

---

## ⭐ Key Highlights

- Implemented end-to-end RAG pipeline (ingestion → embeddings → retrieval → generation)  
- Reduced hallucination using context grounding  
- Designed structured prompts for accurate and reliable responses  
- Enabled multi-document context merging for better answers  

---

## 🧠 Architecture
User Query
↓
Embed Query
↓
Similarity Search (ChromaDB)
↓
Retrieve Relevant Chunks
↓
Generate Response (LLM)
↓
Return Answer with Citations


---

## 🛠️ Tech Stack

- **Backend:** FastAPI, Python  
- **Frontend:** Next.js, Tailwind CSS  
- **LLM:** Google Gemini  
- **Vector Database:** ChromaDB  

---

## ⚙️ Setup

### Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

**Create .env file:**
GOOGLE_API_KEY=your_api_key
CHROMA_PERSIST_DIR=./chroma_db
UPLOAD_DIR=./uploads

**Frontend**
cd frontend
npm install

**Create .env.local:**

NEXT_PUBLIC_API_URL=http://localhost:8000

**Start Backend**
cd backend
uvicorn app.main:app --reload

**Start Frontend**
cd frontend
npm run dev
