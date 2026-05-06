from pydantic import BaseModel, Field
from typing import List, Optional

class IngestResponse(BaseModel):
    document_id: str
    chunks_processed: int
    status: str = "success"

class Citation(BaseModel):
    page_number: str
    text: str

class AskRequest(BaseModel):
    question: str
    limit: Optional[int] = 5

class AskResponse(BaseModel):
    answer: str
    citations: List[Citation]
    status: str = "success"

class HealthResponse(BaseModel):
    status: str
    environment: str
