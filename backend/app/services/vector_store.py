from __future__ import annotations

import json
import logging
from pathlib import Path
from threading import Lock

import numpy as np

from app.config import CHROMA_PATH
from app.services.chunker import Chunk
from app.services.embeddings import get_embeddings, get_query_embedding
from app.services.pdf_processor import clean_extracted_text

logger = logging.getLogger(__name__)

STORE_FILE = CHROMA_PATH / "vector_store.json"
_lock = Lock()

_store: dict | None = None


def _empty_store() -> dict:
    return {"ids": [], "documents": [], "metadatas": [], "embeddings": []}


def _load_store() -> dict:
    global _store
    if _store is not None:
        return _store
    if STORE_FILE.exists():
        try:
            _store = json.loads(STORE_FILE.read_text(encoding="utf-8"))
            for key in ("ids", "documents", "metadatas", "embeddings"):
                _store.setdefault(key, [])
        except Exception:
            logger.warning("Corrupt store file, starting fresh")
            _store = _empty_store()
    else:
        _store = _empty_store()
    return _store


def _save_store() -> None:
    STORE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STORE_FILE.write_text(json.dumps(_store), encoding="utf-8")


def _cosine_similarity(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Cosine similarity between vector *a* (1-D) and matrix *b* (N x D)."""
    if b.shape[0] == 0:
        return np.array([])
    dot = b @ a
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b, axis=1)
    denom = norm_a * norm_b
    denom[denom == 0] = 1e-10
    return dot / denom


def add_document(doc_id: str, chunks: list[Chunk]) -> int:
    if not chunks:
        return 0

    with _lock:
        store = _load_store()
        texts = [c.text for c in chunks]
        embeddings = get_embeddings(texts)
        for i, chunk in enumerate(chunks):
            cid = f"{doc_id}_chunk_{i}"
            store["ids"].append(cid)
            store["documents"].append(chunk.text)
            store["metadatas"].append(chunk.metadata.to_dict())
            store["embeddings"].append(embeddings[i])
        _save_store()

    return len(chunks)


def query(query_text: str, n_results: int = 5, document_filter: str | None = None) -> dict:
    with _lock:
        store = _load_store()

    ids = store["ids"]
    documents = store["documents"]
    metadatas = store["metadatas"]
    embeddings = store["embeddings"]

    if document_filter:
        indices = [i for i, m in enumerate(metadatas) if m.get("document_name") == document_filter]
    else:
        indices = list(range(len(ids)))

    if not indices:
        return {"documents": [[]], "metadatas": [[]], "distances": [[]]}

    subset_embs = np.array([embeddings[i] for i in indices], dtype=np.float32)
    query_emb = np.array(get_query_embedding(query_text), dtype=np.float32)

    similarities = _cosine_similarity(query_emb, subset_embs)
    k = min(n_results, len(indices))
    top_k_local = np.argsort(similarities)[::-1][:k]

    result_docs, result_metas, result_dists = [], [], []
    for local_idx in top_k_local:
        orig_idx = indices[local_idx]
        result_docs.append(clean_extracted_text(documents[orig_idx]))
        result_metas.append(metadatas[orig_idx])
        result_dists.append(float(1 - similarities[local_idx]))

    return {"documents": [result_docs], "metadatas": [result_metas], "distances": [result_dists]}


def delete_document(doc_id: str) -> None:
    with _lock:
        store = _load_store()
        keep = [
            i for i, m in enumerate(store["metadatas"])
            if m.get("document_name") != doc_id and not store["ids"][i].startswith(doc_id)
        ]
        for key in ("ids", "documents", "metadatas", "embeddings"):
            store[key] = [store[key][i] for i in keep]
        _save_store()


def list_documents() -> list[dict]:
    with _lock:
        store = _load_store()

    doc_counts: dict[str, int] = {}
    for meta in store["metadatas"]:
        name = meta.get("document_name", "unknown")
        doc_counts[name] = doc_counts.get(name, 0) + 1

    return [{"id": name, "name": name, "num_chunks": count} for name, count in doc_counts.items()]


def get_document_chunks(doc_name: str) -> list[dict]:
    with _lock:
        store = _load_store()

    chunks = []
    for doc, meta in zip(store["documents"], store["metadatas"]):
        if meta.get("document_name") == doc_name:
            chunks.append({"text": clean_extracted_text(doc), "metadata": meta})

    chunks.sort(key=lambda c: c["metadata"].get("chunk_index", 0))
    return chunks
