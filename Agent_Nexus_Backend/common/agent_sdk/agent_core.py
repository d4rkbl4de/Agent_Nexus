from typing import TypedDict, Callable, List, Optional, Dict, Any
from langgraph.graph import StateGraph, END
from common.schemas import AgentState, AnalysisResult, ActionItem
from common.agents.llm_provider import get_llm, LLMProvider
from common.db.postgres import get_db, PostgresClient
from common.db.postgres import save_analysis_result

async def summarize_node(state: AgentState) -> Dict[str, Any]:
    llm_provider: LLMProvider = get_llm()
    transcript = state['transcript']
    
    has_action_items = True
    
    simulated_result = AnalysisResult(
        summary="Initial summary draft: Key decisions were made regarding Q4 roadmap and budget.",
        key_decisions=["Approved Q4 budget", "Delegated design to John"],
        action_items=[
            ActionItem(task_description="Finalize design mockups", assigned_to="John", due_date="Next Monday")
        ] if has_action_items else []
    )
    
    if simulated_result.action_items:
        next_step = "refine"
    else:
        next_step = "persist"
        
    return {
        "analysis_result": simulated_result,
        "next_step": next_step
    }

async def refine_node(state: AgentState) -> Dict[str, Any]:
    llm_provider: LLMProvider = get_llm()
    transcript = state['transcript']
    analysis_result: AnalysisResult = state['analysis_result']
    
    analysis_result.summary += " (Refined for detail and clarity)."

    return {
        "analysis_result": analysis_result,
        "next_step": "persist"
    }

async def persistence_node(state: AgentState) -> Dict[str, Any]:
    
    return {"next_step": "end"}

def router_node(state: AgentState) -> str:
    next_step = state['next_step']
    if next_step == "summarize":
        return "summarize"
    elif next_step == "refine":
        return "refine"
    elif next_step == "persist":
        return "persist"
    else:
        return END

def build_insightmate_graph() -> StateGraph:
    
    class InsightMateGraphState(TypedDict):
        transcript: str
        analysis_result: Optional[AnalysisResult]
        next_step: str

    workflow = StateGraph(InsightMateGraphState)

    workflow.add_node("summarize", summarize_node)
    workflow.add_node("refine", refine_node)
    workflow.add_node("persist", persistence_node)

    workflow.set_entry_point("summarize")

    workflow.add_conditional_edges(
        "summarize", 
        router_node,
        {
            "refine": "refine",
            "persist": "persist"
        }
    )

    workflow.add_edge("refine", "persist") 

    workflow.add_edge("persist", END)

    return workflow.compile()