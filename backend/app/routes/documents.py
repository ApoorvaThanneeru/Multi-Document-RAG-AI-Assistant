import logging
import uuid
from pathlib import Path

from fastapi import APIRouter, HTTPException, UploadFile, File

from app.config import settings, UPLOAD_PATH
from app.models.schemas import DocumentInfo, UploadResponse
from app.services.pdf_processor import extract_text_from_pdf
from app.services.chunker import chunk_pages
from app.services import vector_store

logger = logging.getLogger(__name__)
router = APIRouter()

MAX_SIZE = settings.MAX_FILE_SIZE_MB * 1024 * 1024


@router.post("/upload", response_model=UploadResponse)
async def upload_document(file: UploadFile = File(...)):
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted.")

    content = await file.read()
    if len(content) > MAX_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size is {settings.MAX_FILE_SIZE_MB}MB.",
        )

    safe_name = file.filename
    file_path = UPLOAD_PATH / f"{uuid.uuid4().hex}_{safe_name}"

    try:
        file_path.write_bytes(content)
        pages = extract_text_from_pdf(file_path)
        chunks = chunk_pages(pages, document_name=safe_name)
        doc_id = safe_name
        vector_store.delete_document(doc_id)
        num_stored = vector_store.add_document(doc_id, chunks)

        return UploadResponse(
            document_id=doc_id,
            name=safe_name,
            num_chunks=num_stored,
            message=f"Successfully processed '{safe_name}' into {num_stored} chunks.",
        )
    except ValueError as e:
        if file_path.exists():
            file_path.unlink()
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.exception("Error processing upload")
        if file_path.exists():
            file_path.unlink()
        raise HTTPException(status_code=500, detail=f"Failed to process document: {e}")


@router.get("", response_model=list[DocumentInfo])
async def list_documents():
    try:
        docs = vector_store.list_documents()
        return [DocumentInfo(**d) for d in docs]
    except Exception as e:
        logger.exception("Error listing documents")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{doc_id}")
async def delete_document(doc_id: str):
    try:
        vector_store.delete_document(doc_id)
        # Also clean up uploaded files matching this doc name
        for f in UPLOAD_PATH.iterdir():
            if f.name.endswith(doc_id):
                f.unlink()
        return {"message": f"Document '{doc_id}' deleted successfully."}
    except Exception as e:
        logger.exception("Error deleting document")
        raise HTTPException(status_code=500, detail=str(e))
