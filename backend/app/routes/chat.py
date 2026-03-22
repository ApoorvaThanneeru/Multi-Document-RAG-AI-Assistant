import logging

from fastapi import APIRouter, HTTPException

from app.models.schemas import ChatRequest, ChatResponse, SourceInfo
from app.services.retriever import retrieve, build_context
from app.services.llm import generate_chat_response
from app.services.pdf_processor import clean_extracted_text

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    try:
        chunks = retrieve(request.question, n_results=8)
        context = build_context(chunks)

        chat_history = [msg.model_dump() for msg in request.chat_history] if request.chat_history else []

        answer = generate_chat_response(
            question=request.question,
            context=context,
            chat_history=chat_history,
        )

        sources = []
        seen = set()
        for chunk in chunks:
            key = (chunk.document_name, chunk.page_number)
            if key not in seen:
                seen.add(key)
                cleaned = clean_extracted_text(chunk.text)
                snippet = cleaned[:200] + "..." if len(cleaned) > 200 else cleaned
                sources.append(
                    SourceInfo(
                        document=chunk.document_name,
                        page=chunk.page_number,
                        snippet=snippet,
                    )
                )

        return ChatResponse(answer=answer, sources=sources)

    except Exception as e:
        logger.exception("Error in chat endpoint")
        raise HTTPException(status_code=500, detail=f"Failed to generate response: {e}")
