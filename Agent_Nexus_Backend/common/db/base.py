import uuid
from datetime import datetime
from typing import Any, Dict, Optional, Type, TypeVar
from sqlalchemy import Column, DateTime, String, JSON, Boolean, func
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

T = TypeVar("T", bound="Base")

class Base(DeclarativeBase):
    @declared_attr
    def __tablename__(cls) -> str:
        name = cls.__name__
        return "".join(["_" + c.lower() if c.isupper() else c for c in name]).lstrip("_")

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(),
        index=True
    )
    
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        onupdate=func.now()
    )
    
    is_deleted: Mapped[bool] = mapped_column(
        Boolean, 
        default=False, 
        index=True
    )

    metadata_extra: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON, 
        nullable=True, 
        default=dict
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            c.name: getattr(self, c.name) 
            for c in self.__table__.columns
        }

    @classmethod
    def from_dict(cls: Type[T], data: Dict[str, Any]) -> T:
        valid_columns = {c.name for c in cls.__table__.columns}
        return cls(**{k: v for k, v in data.items() if k in valid_columns})

class AgenticEntity(Base):
    __abstract__ = True
    
    trace_id: Mapped[str] = mapped_column(
        String(64), 
        index=True, 
        nullable=False
    )
    
    lobe_owner: Mapped[str] = mapped_column(
        String(32), 
        index=True, 
        nullable=False
    )
    
    version: Mapped[int] = mapped_column(
        default=1, 
        nullable=False
    )

class SingletonEntity(Base):
    __abstract__ = True
    
    key: Mapped[str] = mapped_column(
        String(128), 
        unique=True, 
        index=True, 
        nullable=False
    )