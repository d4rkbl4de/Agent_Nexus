import uuid
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from common.config.logging import logger
from tracing.context import get_trace_id, get_agent_id

class DelegationContract(BaseModel):
    contract_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    source_lobe: str
    target_lobe: str
    capability_required: str
    payload: Dict[str, Any]
    priority: int = 1
    timeout: int = 30

class DelegationResult(BaseModel):
    contract_id: str
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None

class DelegationManager:
    def __init__(self):
        self.valid_lobes = {"insightmate", "studyflow", "chatbuddy", "autoagent", "gateway"}

    async def delegate_task(self, contract: DelegationContract) -> DelegationResult:
        trace_id = get_trace_id()
        source = contract.source_lobe.lower()
        target = contract.target_lobe.lower()

        logger.info(
            f"DELEGATION_INITIATED | Trace: {trace_id} | From: {source} | "
            f"To: {target} | Action: {contract.capability_required}"
        )

        if source == target:
            logger.error(f"DELEGATION_SELF_REFERENTIAL_ERROR | Lobe: {source}")
            return DelegationResult(
                contract_id=contract.contract_id,
                success=False,
                error="Self-delegation is prohibited."
            )

        if target not in self.valid_lobes:
            logger.error(f"DELEGATION_TARGET_INVALID | Target: {target}")
            return DelegationResult(
                contract_id=contract.contract_id,
                success=False,
                error=f"Target lobe '{target}' is not a valid Hive Mind member."
            )

        try:
            result_data = await self._dispatch_to_bus(contract)
            
            logger.info(f"DELEGATION_SUCCESS | Trace: {trace_id} | Contract: {contract.contract_id}")
            return DelegationResult(
                contract_id=contract.contract_id,
                success=True,
                data=result_data
            )

        except Exception as e:
            logger.critical(
                f"DELEGATION_FATAL | Trace: {trace_id} | "
                f"Contract: {contract.contract_id} | Error: {str(e)}"
            )
            return DelegationResult(
                contract_id=contract.contract_id,
                success=False,
                error=str(e)
            )

    async def _dispatch_to_bus(self, contract: DelegationContract) -> Any:
        return {"status": "dispatched", "task": contract.capability_required}