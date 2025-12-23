from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated
import operator
import json
from common.schemas.agent_hub_schemas import AutoAgentState, AgentStep, AgentTool
from common.agents.tools import get_tool_specs, execute_lobe_api_call

def _call_llm(prompt: str, json_schema=None) -> dict:
    return {}

def node_plan_decomposition(state: AutoAgentState) -> AutoAgentState:
    
    goal = state["goal"]
    
    planning_prompt = f"Decompose the user goal '{goal}' into a list of sequential steps (AgentStep objects)."
    
    generated_steps = []
    
    if not generated_steps:
        generated_steps.append(AgentStep(
            step_id="step_1",
            description=f"Analyze and fulfill the request: {goal}",
            tool=None,
            status='PENDING'
        ))
    
    return {
        "pending_steps": generated_steps,
        "current_step_status": 'PLANNING'
    }

def node_tool_selection(state: AutoAgentState) -> AutoAgentState:
    
    if not state["pending_steps"]:
        return {"current_step_status": 'COMPLETED'}

    current_step = state["pending_steps"][0]
    available_tools = get_tool_specs()
    
    selection_prompt = f"Select the best tool (from {list(available_tools.keys())}) for the step: {current_step.description}"
    
    if "meeting" in current_step.description.lower():
        selected_tool_name = "InsightMate"
    elif "study" in current_step.description.lower():
        selected_tool_name = "StudyFlow"
    else:
        selected_tool_name = None

    if selected_tool_name:
        tool_spec = available_tools.get(selected_tool_name)
        payload = {"user_id": state["user_id"], "data": current_step.description}
        
        selected_tool = AgentTool(
            name=selected_tool_name,
            endpoint=tool_spec["endpoint"],
            payload=payload
        )
        current_step.tool = selected_tool
        
        return {
            "current_step": current_step,
            "current_step_status": 'TOOL_SELECTION'
        }
    
    return {
        "current_step": current_step,
        "current_step_status": 'COMPLETED'
    }

def node_execute_lobe_api(state: AutoAgentState) -> AutoAgentState:
    
    current_step = state["current_step"]
    
    if current_step and current_step.tool:
        result = execute_lobe_api_call(current_step.tool.endpoint, current_step.tool.payload)
        
        new_history = state["history"] + [f"Executed: {current_step.tool.name} with result: {result}"]
        
        pending_steps = state["pending_steps"][1:]
        
        return {
            "history": new_history,
            "pending_steps": pending_steps,
            "current_step_status": 'EXECUTING'
        }
    
    return {"current_step_status": 'FAILED'}

def node_check_completion(state: AutoAgentState) -> str:
    
    if not state["pending_steps"] and state["current_step_status"] in ['COMPLETED', 'EXECUTING']:
        return "complete"
    else:
        return "continue"

def create_planning_agent():
    workflow = StateGraph(AutoAgentState)

    workflow.add_node("plan_decomposition", node_plan_decomposition)
    workflow.add_node("tool_selection", node_tool_selection)
    workflow.add_node("execute_lobe_api", node_execute_lobe_api)

    workflow.set_entry_point("plan_decomposition")

    workflow.add_edge("plan_decomposition", "tool_selection")
    
    workflow.add_conditional_edges(
        "tool_selection",
        node_check_completion,
        {
            "continue": "execute_lobe_api",
            "complete": END,
        }
    )
    
    workflow.add_edge("execute_lobe_api", "tool_selection")

    app = workflow.compile()
    return app