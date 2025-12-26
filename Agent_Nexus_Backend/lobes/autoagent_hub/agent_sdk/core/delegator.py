import asyncio
import uuid
from typing import Any, Dict, List, Optional
from datetime import datetime

from common.config.logging import logger
from common.schemas.errors import AppError
from common.messaging.publisher import MessagePublisher
from lobes.autoagent_hub.agent_sdk.registry import HubAgentRegistry

class HubDelegator:
    def __init__(self):
        self.registry = HubAgentRegistry()
        self.publisher = MessagePublisher()
        self._delegation_map: Dict[str, List[str]] = {}

    async def delegate_task(
        self,
        parent_agent_id: str,
        target_lobe: str,
        task_type: str,
        payload: Dict[str, Any],
        trace_id: str
    ) -> Dict[str, Any]:
        delegation_id = str(uuid.uuid4())
        logger.info(f"DELEGATION_INITIATED | From: {parent_agent_id} | To Lobe: {target_lobe} | ID: {delegation_id}")

        try:
            if not await self._verify_delegation_policy(parent_agent_id, target_lobe, task_type):
                raise AppError.policy_violation(
                    message=f"Agent {parent_agent_id} is not authorized to delegate to {target_lobe}",
                    trace_id=trace_id,
                    policy_name="DelegationAuthorization"
                )

            self._delegation_map.setdefault(parent_agent_id, []).append(delegation_id)

            routing_key = f"{target_lobe}.tasks.{task_type}"
            message = {
                "delegation_id": delegation_id,
                "parent_id": parent_agent_id,
                "trace_id": trace_id,
                "payload": payload,
                "timestamp": datetime.utcnow().isoformat()
            }

            await self.publisher.publish_event(
                topic=routing_key,
                payload=message
            )

            logger.info(f"DELEGATION_DISPATCHED | Key: {routing_key} | ID: {delegation_id}")
            
            return {
                "delegation_id": delegation_id,
                "status": "DISPATCHED",
                "target_lobe": target_lobe,
                "trace_id": trace_id
            }

        except Exception as e:
            logger.error(f"DELEGATION_FAILURE | ID: {delegation_id} | Error: {str(e)}")
            raise

    async def _verify_delegation_policy(
        self, 
        agent_id: str, 
        target_lobe: str, 
        task_type: str
    ) -> bool:
        agent = await self.registry.get_agent(agent_id)
        if not agent:
            return False
            
        return await agent.policy_engine.check_permission(
            action="delegate_task",
            resource=target_lobe,
            context={"task_type": task_type}
        )

    async def get_active_delegations(self, agent_id: str) -> List[str]:
        return self._delegation_map.get(agent_id, [])

    async def revoke_delegation(self, delegation_id: str, reason: str):
        logger.warning(f"DELEGATION_REVOKED | ID: {delegation_id} | Reason: {reason}")
        await self.publisher.publish_event(
            topic="system.management.revocation",
            payload={"delegation_id": delegation_id, "reason": reason}
        )