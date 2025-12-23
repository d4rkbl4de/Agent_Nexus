import logging
from .postgres import engine, SessionLocal, get_db
from .base import Base
from .session import tenant_context, get_tenant_session
from .crud import BaseCRUD
from .exceptions import DatabaseError, EntityNotFoundError

logger = logging.getLogger(__name__)

try:
    from .models import User, Organization
    from .mixins import TimestampMixin, AuditMixin
    from .study_models import StudyPlan, Quiz, Progress
    from .chat_models import ChatSession, Message, AgentMemory
except ImportError as e:
    logger.critical(f"Database model registration failed: {str(e)}")
    raise

__all__ = [
    "engine",
    "SessionLocal",
    "get_db",
    "Base",
    "tenant_context",
    "get_tenant_session",
    "BaseCRUD",
    "DatabaseError",
    "EntityNotFoundError",
    "User",
    "Organization",
    "TimestampMixin",
    "AuditMixin",
    "StudyPlan",
    "Quiz",
    "Progress",
    "ChatSession",
    "Message",
    "AgentMemory",
]