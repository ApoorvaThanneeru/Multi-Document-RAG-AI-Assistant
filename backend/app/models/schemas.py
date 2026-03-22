from pydantic import BaseModel


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    question: str
    chat_history: list[ChatMessage] = []


class SourceInfo(BaseModel):
    document: str
    page: int
    snippet: str


class ChatResponse(BaseModel):
    answer: str
    sources: list[SourceInfo]


class SummarizeRequest(BaseModel):
    document_id: str


class SummarizeResponse(BaseModel):
    document: str
    summary: str


class DocumentInfo(BaseModel):
    id: str
    name: str
    num_chunks: int


class UploadResponse(BaseModel):
    document_id: str
    name: str
    num_chunks: int
    message: str
