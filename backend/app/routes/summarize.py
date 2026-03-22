import logging

from fastapi import APIRouter, HTTPException

from app.models.schemas import SummarizeRequest, SummarizeResponse
from app.services.vector_store import get_document_chunks
from app.services.llm import generate_summary

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/summarize", response_model=SummarizeResponse)
async def summarize_document(request: SummarizeRequest):
    if not request.document_id.strip():
        raise HTTPException(status_code=400, detail="Document ID cannot be empty.")

    try:
        chunks = get_document_chunks(request.document_id)
        if not chunks:
            raise HTTPException(
                status_code=404,
                detail=f"No document found with ID '{request.document_id}'.",
            )

        full_text = "\n\n".join(
            f"[Page {c['metadata'].get('page_number', '?')}]\n{c['text']}"
            for c in chunks
        )

        # Truncate if too long for the model context
        max_chars = 30000
        if len(full_text) > max_chars:
            full_text = full_text[:max_chars] + "\n\n[... document truncated for summarization ...]"

        summary = generate_summary(
            document_name=request.document_id,
            content=full_text,
        )

        return SummarizeResponse(document=request.document_id, summary=summary)

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error in summarize endpoint")
        raise HTTPException(status_code=500, detail=f"Failed to summarize document: {e}")
