from fastapi import APIRouter, status
from common.schemas.agent_hub_schemas import AgentInput
from AutoAgent_Hub.tasks import run_planning_agent

router = APIRouter()

@router.post("/process-goal", status_code=status.HTTP_202_ACCEPTED)
async def process_user_goal(agent_input: AgentInput):
    task = run_planning_agent.send(agent_input.user_id, agent_input.goal)
    return {
        "message": "Planning agent started asynchronously",
        "task_id": task.message_id,
        "status_url": f"/tasks/status/{task.message_id}"
    }

@router.get("/health")
async def health_check():
    return {"status": "ok"}