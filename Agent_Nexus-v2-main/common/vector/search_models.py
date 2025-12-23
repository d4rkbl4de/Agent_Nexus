from pydantic import BaseModel, Field
from typing import Dict, Any, List
from uuid import uuid4


class VectorPoint(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    vector: List[float]
    payload: Dict[str, Any]


class SearchResult(BaseModel):
    id: str
    score: float
    payload: Dict[str, Any]
