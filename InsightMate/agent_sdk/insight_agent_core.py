from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated
import operator
from common.schemas.insight_schemas import InsightAgentState

def create_insight_agent():
    workflow = StateGraph(InsightAgentState)

    workflow.add_node("data_validation", lambda state: {"action": "VALIDATE"})
    workflow.add_node("summary_generation", lambda state: {"action": "SUMMARIZE"})
    workflow.add_node("action_item_extraction", lambda state: {"action": "EXTRACT_ACTIONS"})
    workflow.add_node("memory_persistence", lambda state: {"action": "PERSIST"})

    workflow.set_entry_point("data_validation")
    workflow.add_edge("data_validation", "summary_generation")
    workflow.add_edge("summary_generation", "action_item_extraction")
    workflow.add_edge("action_item_extraction", "memory_persistence")
    workflow.add_edge("memory_persistence", END)

    app = workflow.compile()
    return app