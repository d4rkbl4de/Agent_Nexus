from langgraph.graph import StateGraph, END
from typing import TypedDict, Dict, Optional
from common.schemas.agent_hub_schemas import GoalPlan, PlanningStep
from common.agents.internal_tools import INTERNAL_TOOL_CLIENT
import asyncio
import os

class AutoAgentState(TypedDict):
    user_id: str
    goal: str
    plan: Optional[GoalPlan]
    current_step: int
    tool_call_result: Optional[Dict]
    final_output: Optional[str]
    error_message: Optional[str]

def llm_plan_goal(state: AutoAgentState) -> Dict:
    print(f"Agent Planning: Decomposing Goal: {state['goal']}")
    mock_plan_data = {
        "user_goal": state["goal"],
        "plan_steps": [
            {
                "step_number": 1,
                "description": "Call InsightMate to analyze the current market report for key trends.",
                "target_lobe": "InsightMate",
                "tool_input": {"document_id": "market_report_Q4_2025", "analysis_type": "trends"}
            },
            {
                "step_number": 2,
                "description": "Call ChatBuddyPlus to draft a summary email for the executive team based on the trends found in step 1.",
                "target_lobe": "ChatBuddyPlus",
                "tool_input": {"prompt": "Summarize the findings from step 1 for executives."}
            }
        ]
    }
    goal_plan = GoalPlan.model_validate(mock_plan_data)
    return {"plan": goal_plan, "current_step": 1}

async def execute_step(state: AutoAgentState) -> Dict:
    step_index = state["current_step"] - 1
    current_plan: GoalPlan = state["plan"]
    if step_index >= len(current_plan.plan_steps):
        return {"error_message": "Execution index out of bounds, planning error."}
    current_step_data: PlanningStep = current_plan.plan_steps[step_index]
    print(f"Executing Step {state['current_step']}: Calling {current_step_data.target_lobe.value}")
    try:
        if os.environ.get("ENV") == "prod":
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, lambda: asyncio.run(INTERNAL_TOOL_CLIENT.execute_tool(
                current_step_data.target_lobe,
                current_step_data.tool_input
            )))
        else:
            await asyncio.sleep(1) 
            result = await INTERNAL_TOOL_CLIENT.execute_tool(
                current_step_data.target_lobe,
                current_step_data.tool_input
            )
    except Exception as e:
        return {"error_message": f"Execution failed at step {state['current_step']}: {str(e)}"}
    new_step = state["current_step"] + 1
    return {"tool_call_result": result, "current_step": new_step}

def llm_aggregate_results(state: AutoAgentState) -> Dict:
    print("Aggregating final output using LLM synthesis.")
    final_answer = (
        f"Goal: '{state['goal']}' successfully executed across multiple Lobes. "
        f"Result from the last step ({state['tool_call_result']['task_id']}) has been secured."
    )
    return {"final_output": final_answer}

def should_continue(state: AutoAgentState) -> str:
    current_step = state["current_step"]
    plan_length = len(state["plan"].plan_steps) if state["plan"] else 0
    if state.get("error_message"):
        return "error"
    if current_step <= plan_length:
        return "continue"
    else:
        return "finish"

class PlanningAgentCore:
    def __init__(self):
        self.graph = self._build_graph()

    def _build_graph(self):
        workflow = StateGraph(AutoAgentState)
        workflow.add_node("plan_goal", llm_plan_goal)
        workflow.add_node("execute_step", execute_step)
        workflow.add_node("aggregate_results", llm_aggregate_results)
        workflow.set_entry_point("plan_goal")
        workflow.add_edge("plan_goal", "execute_step")
        workflow.add_conditional_edges(
            "execute_step",
            should_continue,
            {
                "continue": "execute_step",
                "finish": "aggregate_results",
                "error": END
            }
        )
        workflow.add_edge("aggregate_results", END)
        return workflow.compile()

PLANNING_AGENT_CORE = PlanningAgentCore()