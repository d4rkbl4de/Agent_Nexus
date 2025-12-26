import uuid
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from common.schemas.api_response import APIResponse
from common.schemas.errors import AppError, ErrorCategory
from common.config.logging import logger
from lobes.autoagent_hub.api.v1.schemas import (
    TaskCreateRequest, 
    TaskStatusResponse, 
    AgentRegistryResponse,
    OrchestrationPlanResponse
)
from lobes.autoagent_hub.tasks import processor
from lobes.autoagent_hub.agent_sdk.registry import hub_agent_registry

router = APIRouter()

@router.post("/tasks", response_model=APIResponse[TaskStatusResponse], status_code=status.HTTP_202_ACCEPTED)
async def create_orchestration_task(
    payload: TaskCreateRequest, 
    background_tasks: BackgroundTasks
):
    trace_id = str(uuid.uuid4())
    task_id = str(uuid.uuid4())
    
    logger.info(f"API_TASK_RECEIVED | Task: {task_id} | Agent: {payload.agent_id} | Trace: {trace_id}")
    
    background_tasks.add_task(
        processor.process_hub_task, 
        task_data={**payload.model_dump(), "task_id": task_id},
        trace_id=trace_id
    )
    
    return APIResponse(
        success=True,
        trace_id=trace_id,
        data=TaskStatusResponse(
            task_id=task_id,
            status="QUEUED",
            message="Orchestration task accepted and delegated to background worker."
        )
    )

@router.get("/agents", response_model=APIResponse[List[AgentRegistryResponse]])
async def list_hub_agents():
    trace_id = str(uuid.uuid4())
    try:
        agents = await hub_agent_registry.list_available_agents()
        return APIResponse(
            success=True,
            trace_id=trace_id,
            data=[AgentRegistryResponse(**a) for a in agents]
        )
    except Exception as e:
        logger.error(f"API_AGENT_LIST_FAILED | Trace: {trace_id} | Error: {str(e)}")
        raise AppError(
            category=ErrorCategory.INTERNAL,
            trace_id=trace_id,
            error={"code": "HUB_AGENT_LIST_001", "message": "Failed to retrieve agent registry."}
        )

@router.get("/tasks/{task_id}", response_model=APIResponse[TaskStatusResponse])
async def get_task_status(task_id: str):
    trace_id = str(uuid.uuid4())

    return APIResponse(
        success=True,
        trace_id=trace_id,
        data=TaskStatusResponse(
            task_id=task_id,
            status="PROCESSING",
            message="Task is currently being handled by the Orchestration Supervisor."
        )
    )

@router.post("/tasks/{task_id}/approve", response_model=APIResponse[Dict[str, Any]])
async def approve_task_step(task_id: str, step_id: str):
    trace_id = str(uuid.uuid4())
    logger.info(f"API_STEP_APPROVED | Task: {task_id} | Step: {step_id} | Trace: {trace_id}")
    
    return APIResponse(
        success=True,
        trace_id=trace_id,
        data={"status": "RESUMED", "task_id": task_id, "step_id": step_id}
    )