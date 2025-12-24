from typing import TypedDict, List, Literal, Optional
from langgraph.graph import StateGraph, START, END
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from common.agents.tools import get_user_profile_summary_tool, update_user_profile_tool, save_conversation_message_tool
from common.schemas.chat_schemas import ChatResponse
from langchain_core.messages import HumanMessage
import json
from pydantic import Field

class ChatAgentState(TypedDict):
    user_id: str
    session_id: str
    message: str
    
    user_profile_json: str
    
    chat_response: ChatResponse | None
    
    tool_update_needed: Literal['YES', 'NO']
    profile_facts_to_add: Optional[List[str]]

LLM = ChatGoogleGenerativeAI(model="gemini-2.5-pro") 

def retrieve_profile(state: ChatAgentState) -> ChatAgentState:
    profile_json = get_user_profile_summary_tool(user_id=state['user_id'])
    
    save_conversation_message_tool(
        user_id=state['user_id'],
        session_id=state['session_id'],
        message_type='USER',
        content=state['message']
    )
    
    return {"user_profile_json": profile_json}

def generate_and_critique_response(state: ChatAgentState) -> ChatAgentState:
    system_prompt = (
        "You are ChatBuddy+, a personal, empathetic AI assistant. Your primary goal is to maintain a "
        "personalized, helpful conversation. ALWAYS incorporate the user's personality and facts "
        "from the User Profile when relevant."
    )
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("system", f"CURRENT USER PROFILE:\n{state['user_profile_json']}"),
        ("human", f"USER MESSAGE: {state['message']}\n\n"
                  "1. Formulate a personalized response.\n"
                  "2. Analyze the user message for any new, persistent personal facts (e.g., 'I am left-handed', 'I love Goku').\n"
                  "3. If new facts are found, list them in the 'profile_facts_to_add' field. Otherwise, leave it empty. Set 'tool_update_needed' accordingly."
        )
    ])
    
    class ChatCritique(ChatResponse):
        tool_update_needed: Literal['YES', 'NO'] = Field(description="Set to YES if the message contains new facts that must be added to the user's profile.")
        profile_facts_to_add: List[str] = Field(description="A list of 1-3 new, persistent facts or preferences learned about the user.")
    
    chain = prompt | LLM.with_structured_output(ChatCritique)
    critique_result = chain.invoke({})
    
    return {
        "chat_response": critique_result,
        "tool_update_needed": critique_result.tool_update_needed,
        "profile_facts_to_add": critique_result.profile_facts_to_add
    }

def update_profile_memory(state: ChatAgentState) -> ChatAgentState:
    if not state.get('profile_facts_to_add'):
        return {}

    profile = json.loads(state['user_profile_json'])
    existing_facts = profile.get('key_facts', [])
    
    all_facts = list(set(existing_facts + state['profile_facts_to_add']))
    
    update_user_profile_tool(
        user_id=state['user_id'],
        name=profile.get('name', state['user_id']),
        key_interests=profile.get('key_interests', []),
        key_facts=all_facts
    )
    
    return {}

def route_to_update(state: ChatAgentState) -> str:
    if state.get('tool_update_needed') == 'YES':
        return "update_memory"
    return "end_chat"

def create_chat_graph():
    workflow = StateGraph(ChatAgentState)
    
    workflow.add_node("retrieve", retrieve_profile)
    workflow.add_node("generate_critique", generate_and_critique_response)
    workflow.add_node("update_memory", update_profile_memory)
    
    workflow.set_entry_point("retrieve")
    workflow.add_edge("retrieve", "generate_critique")
    
    workflow.add_conditional_edges(
        "generate_critique",
        route_to_update,
        {"update_memory": "update_memory", "end_chat": END}
    )
    
    workflow.add_edge("update_memory", END)
    
    return workflow.compile()