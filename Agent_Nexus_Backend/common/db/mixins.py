from datetime import datetime
from sqlalchemy import Column, DateTime, String
from sqlalchemy.orm import declarative_mixin

@declarative_mixin
class AgenticTraceMixin:
    """
    Superpower Mixin for the Hive Mind.
    Adds tracking fields to any model to ensure we can audit 
    which agent created or modified a record.
    """
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    
    created_by_agent = Column(String(100), nullable=True, default="system_init")
    trace_id = Column(String(255), nullable=True) 
    parent_trace_id = Column(String(255), nullable=True)
    root_trace_id = Column(String(255), nullable=True) 
    session_id = Column(String(255), nullable=True)
    conversation_id = Column(String(255), nullable=True)
    user_id = Column(String(255), nullable=True)
    organization_id = Column(String(255), nullable=True)
    project_id = Column(String(255), nullable=True)
    workspace_id = Column(String(255), nullable=True)
    environment_id = Column(String(255), nullable=True)
    run_id = Column(String(255), nullable=True)
    task_id = Column(String(255), nullable=True)
    agent_id = Column(String(255), nullable=True)
    tool_id = Column(String(255), nullable=True)
    action_id = Column(String(255), nullable=True)

