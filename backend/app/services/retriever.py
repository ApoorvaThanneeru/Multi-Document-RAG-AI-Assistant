import logging

from app.services import vector_store

logger = logging.getLogger(__name__)


class RetrievedChunk:
    def __init__(self, text: str, document_name: str, page_number: int, distance: float):
        self.text = text
        self.document_name = document_name
        self.page_number = page_number
        self.distance = distance


def retrieve(
    query: str, n_results: int = 5, document_filter: str | None = None
) -> list[RetrievedChunk]:
    """Retrieve the most relevant chunks for a query."""
    results = vector_store.query(
        query, n_results=n_results, document_filter=document_filter
    )

    chunks: list[RetrievedChunk] = []
    if not results["documents"] or not results["documents"][0]:
        return chunks

    for doc, meta, dist in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        chunks.append(
            RetrievedChunk(
                text=doc,
                document_name=meta.get("document_name", "unknown"),
                page_number=meta.get("page_number", 0),
                distance=dist,
            )
        )

    return chunks


def build_context(chunks: list[RetrievedChunk]) -> str:
    """Format retrieved chunks into a context string for the LLM prompt."""
    if not chunks:
        return "No relevant context found in the uploaded documents."

    context_parts = []
    for i, chunk in enumerate(chunks, 1):
        context_parts.append(
            f"[Source {i}: {chunk.document_name}, Page {chunk.page_number}]\n{chunk.text}"
        )

    return "\n\n---\n\n".join(context_parts)
