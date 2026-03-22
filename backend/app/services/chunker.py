from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.config import settings
from app.services.pdf_processor import PageContent


class ChunkMetadata:
    def __init__(self, document_name: str, page_number: int, chunk_index: int):
        self.document_name = document_name
        self.page_number = page_number
        self.chunk_index = chunk_index

    def to_dict(self) -> dict:
        return {
            "document_name": self.document_name,
            "page_number": self.page_number,
            "chunk_index": self.chunk_index,
        }


class Chunk:
    def __init__(self, text: str, metadata: ChunkMetadata):
        self.text = text
        self.metadata = metadata


def chunk_pages(pages: list[PageContent], document_name: str) -> list[Chunk]:
    """Split page contents into overlapping chunks with metadata."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.CHUNK_SIZE,
        chunk_overlap=settings.CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    chunks: list[Chunk] = []
    global_index = 0

    for page in pages:
        page_chunks = splitter.split_text(page.text)
        for text in page_chunks:
            metadata = ChunkMetadata(
                document_name=document_name,
                page_number=page.page_number,
                chunk_index=global_index,
            )
            chunks.append(Chunk(text=text, metadata=metadata))
            global_index += 1

    return chunks
