import logging
from typing import Any

from common.db.postgres import Base

logger = logging.getLogger(__name__)

try:
    from common.db.models import User, AgentState, AuditLog
    
    from common.db.study_models import QuizAttempt, StudyPlan, Quiz, ProgressTracker
    
    from common.db.chat_models import Conversation, Message, ContextWindow
    
    logger.info("📡 All Hive Mind models successfully registered for migration.")

except ImportError as e:
    logger.warning(f"⚠️ Partial schema registration: {e}")

target_metadata = Base.metadata

__all__ = [
    "Base",
    "target_metadata",
    "User",
    "AgentState",
    "AuditLog",
    "QuizAttempt",
    "StudyPlan",
    "Quiz",
    "ProgressTracker",
    "Conversation",
    "Message",
    "ContextWindow"
]
