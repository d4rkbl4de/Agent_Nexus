import uuid
from typing import Any, Dict, List
from fastapi import APIRouter, Depends, HTTPException, status, Header
from gateway.dependencies import get_current_user, get_db, get_llm_client
from tracing.context import set_trace_id, get_trace_id
from policy.execution_policy import execution_guard
from policy.cost_policy import budget_check
from policy.delegation_policy import DelegationContract, DelegationPolicy
from common.schemas.responses import GenericResponse

router = APIRouter(prefix="/api/v1", tags=["Gateway"])

@router.get("/health", response_model=GenericResponse)
async def health_check():
    return GenericResponse(
        status="success",
        message="Agent Nexus Hive Mind Gateway Operational",
        data={"version": "2.0.0", "status": "healthy"}
    )

@router.post("/execute/{lobe_name}", response_model=GenericResponse)
@execution_guard(max_depth=10, max_tools=5)
@budget_check(estimated_tokens=5000)
async def execute_lobe_task(
    lobe_name: str,
    payload: Dict[str, Any],
    x_trace_id: str = Header(None),
    current_user: Dict = Depends(get_current_user),
    db: Any = Depends(get_db),
    llm: Any = Depends(get_llm_client)
):
    trace_id = x_trace_id or str(uuid.uuid4())
    set_trace_id(trace_id)
    
    valid_lobes = ["insightmate", "studyflow", "chatbuddy", "autoagent"]
    if lobe_name.lower() not in valid_lobes:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lobe '{lobe_name}' not found in Hive Mind architecture."
        )

    policy = DelegationPolicy()
    contract = DelegationContract(
        source_lobe="gateway",
        target_lobe=lobe_name.lower(),
        capability_required="external_request_execution"
    )
    
    if not await policy.authorize_delegation(contract):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Delegation policy rejected request execution."
        )

    return GenericResponse(
        status="success",
        message=f"Task accepted by {lobe_name}",
        data={
            "trace_id": trace_id,
            "agent_id": lobe_name,
            "execution_context": "async_polled"
        }
    )

@router.get("/telemetry/{trace_id}", response_model=GenericResponse)
async def get_trace_telemetry(
    trace_id: str,
    current_user: Dict = Depends(get_current_user),
    db: Any = Depends(get_db)
):
    return GenericResponse(
        status="success",
        message="Telemetry data retrieved",
        data={
            "trace_id": trace_id,
            "logs": [],
            "metrics": {"cost_usd": 0.0, "tokens": 0}
        }
    )