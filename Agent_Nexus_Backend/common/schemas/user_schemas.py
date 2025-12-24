from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Dict, Any
from uuid import uuid4
from datetime import datetime


class UserCreate(BaseModel):
    email: EmailStr
    name: str
    preferences: Dict[str, Any] = Field(default_factory=dict)


class UserUpdate(BaseModel):
    name: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = None


class UserRecord(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    email: EmailStr
    name: str
    preferences: Dict[str, Any]
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True
