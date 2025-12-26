import uuid
import asyncio
from typing import Any, Dict, List, Optional
from enum import Enum
from pydantic import BaseModel, Field
from datetime import datetime

from common.config.logging import logger
from common.schemas.errors import AppError, ErrorCategory

class PolicyEffect(str, Enum):
    ALLOW = "ALLOW"
    DENY = "DENY"

class PolicyRule(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    action: str
    resource: str
    effect: PolicyEffect
    conditions: Dict[str, Any] = Field(default_factory=dict)

class PolicyEvaluation(BaseModel):
    allowed: bool
    reason: str
    policy_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class PolicyEngine:
    def __init__(self):
        self._global_policies: List[PolicyRule] = self._load_default_policies()

    def _load_default_policies(self) -> List[PolicyRule]:
        return [
            PolicyRule(
                name="DENY_SENSITIVE_FS",
                action="execute_tool",
                resource="filesystem",
                effect=PolicyEffect.DENY,
                conditions={"path": ["/etc", "/var/log", "/root"]}
            ),
            PolicyRule(
                name="ALLOW_HUB_INTERNAL",
                action="delegate_task",
                resource="*",
                effect=PolicyEffect.ALLOW
            )
        ]

    async def check_permission(
        self, 
        action: str, 
        resource: str, 
        context: Dict[str, Any]
    ) -> bool:
        evaluation = await self.evaluate(action, resource, context)
        if not evaluation.allowed:
            logger.warning(
                f"POLICY_VIOLATION | Action: {action} | Resource: {resource} | Reason: {evaluation.reason}"
            )
        return evaluation.allowed

    async def evaluate(
        self, 
        action: str, 
        resource: str, 
        context: Dict[str, Any]
    ) -> PolicyEvaluation:
        for rule in self._global_policies:
            if self._matches(rule, action, resource, context):
                if rule.effect == PolicyEffect.DENY:
                    return PolicyEvaluation(
                        allowed=False, 
                        reason=f"Explicitly denied by policy: {rule.name}",
                        policy_id=rule.id
                    )
                
                if rule.effect == PolicyEffect.ALLOW:
                    return PolicyEvaluation(
                        allowed=True, 
                        reason=f"Allowed by policy: {rule.name}",
                        policy_id=rule.id
                    )

        return PolicyEvaluation(
            allowed=False, 
            reason="Implicit deny: No matching policy found."
        )

    def _matches(
        self, 
        rule: PolicyRule, 
        action: str, 
        resource: str, 
        context: Dict[str, Any]
    ) -> bool:
        if rule.action != "*" and rule.action != action:
            return False
        
        if rule.resource != "*" and rule.resource != resource:
            return False

        for key, restricted_values in rule.conditions.items():
            current_val = context.get(key)
            if isinstance(restricted_values, list):
                if any(str(current_val).startswith(str(v)) for v in restricted_values):
                    return True
        
        return True

    async def audit_policy_usage(self, trace_id: str):
        logger.info(f"POLICY_AUDIT_REQUESTED | Trace: {trace_id}")