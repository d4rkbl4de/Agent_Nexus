import asyncio
from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from common.config.logging import logger
from common.schemas.errors import AppError, ErrorCategory

class KillSwitchStatus(BaseModel):
    is_active: bool = False
    reason: Optional[str] = None
    triggered_at: Optional[datetime] = None
    triggered_by: Optional[str] = None
    affected_lobes: list[str] = Field(default_factory=lambda: ["*"])

class KillSwitch:
    _instance: Optional['KillSwitch'] = None
    _state: KillSwitchStatus = KillSwitchStatus()
    _lock = asyncio.Lock()

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(KillSwitch, cls).__new__(cls)
        return cls._instance

    async def activate(
        self, 
        reason: str, 
        agent_id: Optional[str] = None, 
        lobes: Optional[list[str]] = None
    ) -> None:
        async with self._lock:
            self._state = KillSwitchStatus(
                is_active=True,
                reason=reason,
                triggered_at=datetime.utcnow(),
                triggered_by=agent_id,
                affected_lobes=lobes or ["*"]
            )
            logger.critical(
                f"KILL_SWITCH_ACTIVATED | Reason: {reason} | Affected: {self._state.affected_lobes}"
            )

    async def deactivate(self) -> None:
        async with self._lock:
            logger.warning("KILL_SWITCH_DEACTIVATED | System Resuming")
            self._state = KillSwitchStatus(is_active=False)

    async def check_execution_safety(self, lobe_name: str) -> None:
        if not self._state.is_active:
            return

        if "*" in self._state.affected_lobes or lobe_name in self._state.affected_lobes:
            logger.error(f"EXECUTION_BLOCKED | Lobe: {lobe_name} | Reason: {self._state.reason}")
            raise AppError(
                message=f"System execution is halted: {self._state.reason}",
                category=ErrorCategory.POLICY_VIOLATION,
                status_code=503,
                retryable=False
            )

    @property
    def current_status(self) -> Dict[str, Any]:
        return self._state.model_dump()

kill_switch = KillSwitch()