from sqlalchemy import Column, String, Text, Boolean, JSON, ForeignKey, func, Integer
from sqlalchemy.orm import relationship
from common.db.base import Base
from common.db.mixins import AgenticTraceMixin

class User(Base, AgenticTraceMixin):
    __tablename__ = 'users'

    id = Column(String, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    full_name = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    
    preferences = Column(JSON, default={}, nullable=False)
    
    account_tier = Column(String(50), default="free")

class AgentState(Base, AgenticTraceMixin):
    __tablename__ = 'agent_states'

    id = Column(String, primary_key=True, index=True)
    agent_id = Column(String(100), index=True, nullable=False)
    user_id = Column(String, ForeignKey('users.id', ondelete="CASCADE"), index=True)
    
    current_state = Column(JSON, nullable=False)
    
    status = Column(String(50), default="idle")
    last_error = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0)

class AuditLog(Base, AgenticTraceMixin):
    __tablename__ = 'audit_logs'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, ForeignKey('users.id', ondelete="SET NULL"), index=True)
    
    action = Column(String(100), nullable=False, index=True)
    lobe = Column(String(50), nullable=False)
    
    input_tokens = Column(Integer, default=0)
    output_tokens = Column(Integer, default=0)
    cost_estimate = Column(String(50), nullable=True)
    
    description = Column(Text, nullable=False)