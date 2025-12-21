from sqlalchemy.orm import declarative_mixin
from sqlalchemy import Column, Integer, DateTime
from datetime import datetime

@declarative_mixin
class IDMixin:
    id = Column(Integer, primary_key=True, index=True)

@declarative_mixin
class TimestampMixin:
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)