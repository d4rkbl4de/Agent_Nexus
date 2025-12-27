from typing import Any, Dict, Optional
from policy.kill_switch import kill_switch, KillSwitch
from decisions.verdict import policy_engine, PolicyEngine
from common.config.logging import logger
from common.schemas.errors import AppError, ErrorCategory

class PolicySentry:
    def __init__(self):
        self.kill_switch = kill_switch
        self.engine = policy_engine

    async def validate_intent(self, proposal: Any) -> Any:
        if self.kill_switch.is_halted():
            raise AppError(
                message="System-wide kill switch active. All agent actions suspended.",
                category=ErrorCategory.POLICY_VIOLATION,
                status_code=503
            )
        
        verdict = await self.engine.evaluate_proposal(proposal)
        
        if verdict.status.value in ["DENIED", "HALTED", "ERROR"]:
            logger.warning(f"POLICY_REJECTION | Trace: {proposal.trace_id} | Reason: {verdict.reasoning}")
            raise AppError(
                message=f"Action denied by policy: {verdict.reasoning}",
                category=ErrorCategory.POLICY_VIOLATION,
                status_code=403
            )
            
        return verdict

    def emergency_stop(self, reason: str):
        self.kill_switch.activate(reason)
        logger.critical(f"EMERGENCY_STOP_TRIGGERED | Reason: {reason}")

    def resume_operations(self):
        self.kill_switch.deactivate()
        logger.info("SYSTEM_OPERATIONS_RESUMED")

policy_sentry = PolicySentry()

__all__ = [
    "policy_sentry",
    "kill_switch",
    "policy_engine",
    "KillSwitch",
    "PolicyEngine"
]