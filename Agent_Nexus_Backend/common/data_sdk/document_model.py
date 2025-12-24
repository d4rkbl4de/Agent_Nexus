from typing import Dict, Any, List
from pydantic import BaseModel, Field
from uuid import uuid4


class Document(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class DocumentChunk(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    document_id: str
    content: str
    index: int
    metadata: Dict[str, Any] = Field(default_factory=dict)
