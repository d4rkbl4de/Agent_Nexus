from dataclasses import dataclass, field
from typing import Dict, Any
from uuid import uuid4
from datetime import datetime


@dataclass(frozen=True)
class MemoryRecord:
    content: str
    role: str
    agent_id: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    id: str = field(default_factory=lambda: str(uuid4()))
    timestamp: datetime = field(default_factory=datetime.utcnow)
