import threading
import uuid
from typing import Any, Dict, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

from common.config.logging import logger
from common.schemas.errors import AppError, ErrorCategory

class SessionState(BaseModel):
    session_id: str
    trace_id: str
    agent_id: str
    lobe: str
    values: Dict[str, Any] = Field(default_factory=dict)
    history: List[Dict[str, Any]] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    model_config = ConfigDict(validate_assignment=True)

class HubStateManager:
    _instance: Optional['HubStateManager'] = None
    _lock = threading.RLock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, '_initialized'):
            self._sessions: Dict[str, SessionState] = {}
            self._session_locks: Dict[str, threading.Lock] = {}
            self._initialized = True

    def create_session(self, agent_id: str, lobe: str, trace_id: str) -> str:
        session_id = str(uuid.uuid4())
        state = SessionState(
            session_id=session_id,
            trace_id=trace_id,
            agent_id=agent_id,
            lobe=lobe
        )
        
        with self._lock:
            self._sessions[session_id] = state
            self._session_locks[session_id] = threading.Lock()
            
        logger.info(f"STATE_SESSION_CREATED | Session: {session_id} | Lobe: {lobe} | Trace: {trace_id}")
        return session_id

    def get_state(self, session_id: str) -> SessionState:
        with self._lock:
            state = self._sessions.get(session_id)
            if not state:
                raise AppError(
                    category=ErrorCategory.NOT_FOUND,
                    error={"code": "STATE_NOT_FOUND", "message": f"Session {session_id} not active"}
                )
            return state

    def update_value(self, session_id: str, key: str, value: Any, trace_id: str):
        lock = self._get_session_lock(session_id)
        with lock:
            state = self.get_state(session_id)
            old_value = state.values.get(key)
            state.values[key] = value
            state.updated_at = datetime.utcnow()
            
            state.history.append({
                "timestamp": state.updated_at.isoformat(),
                "trace_id": trace_id,
                "action": "UPDATE_VALUE",
                "key": key,
                "old": old_value,
                "new": value
            })
            
        logger.debug(f"STATE_VALUE_UPDATED | Session: {session_id} | Key: {key} | Trace: {trace_id}")

    def append_history(self, session_id: str, event: Dict[str, Any]):
        lock = self._get_session_lock(session_id)
        with lock:
            state = self.get_state(session_id)
            event["timestamp"] = datetime.utcnow().isoformat()
            state.history.append(event)
            state.updated_at = datetime.utcnow()

    def _get_session_lock(self, session_id: str) -> threading.Lock:
        with self._lock:
            if session_id not in self._session_locks:
                self._session_locks[session_id] = threading.Lock()
            return self._session_locks[session_id]

    def cleanup_session(self, session_id: str):
        with self._lock:
            if session_id in self._sessions:
                del self._sessions[session_id]
                self._session_locks.pop(session_id, None)
                logger.info(f"STATE_SESSION_PURGED | Session: {session_id}")

hub_state_manager = HubStateManager()