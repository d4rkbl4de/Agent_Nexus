from typing import TypedDict, List, Literal
from langgraph.graph import StateGraph, START, END
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from common.agents.tools import vector_search_tool
from common.schemas.study_schemas import StudyResultSchema
from common.agents.tools import save_quiz_attempt_tool


class StudyAgentState(TypedDict):
    user_id: str
    query: str
    
    retrieved_documents: List[str]
    
    study_plan_result: StudyResultSchema | None
    quiz_attempt: float
    
    critique_needed: Literal['YES', 'NO', 'N/A']
    loop_count: int



LLM = ChatGoogleGenerativeAI(model="gemini-2.5-flash")


def retrieve_rag_context(state: StudyAgentState) -> StudyAgentState:
    print(f"--- STUDYFLOW NODE: Retrieving Context for query: {state['query'][:30]}... ---")
    results = vector_search_tool(query=state['query']) 
    context_list = [r['content'] for r in results if r]
    print(f"--- STUDYFLOW: Retrieved {len(context_list)} chunks. ---")
    return {"retrieved_documents": context_list}

def generate_study_plan(state: StudyAgentState) -> StudyAgentState:
    print("--- STUDYFLOW NODE: Generating Grounded Study Result (Structured Output) ---")
    context_str = "\n---\n".join(state['retrieved_documents'])
    system_prompt = (
        "You are an expert Study Assistant. Your task is to answer the user's query truthfully and concisely "
        "using ONLY the provided context from the study documents. If the context does not contain the answer, "
        "state that you lack the necessary information and set confidence_score to 0.1."
    )
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", 
         f"QUERY: {state['query']}\n\n"
         f"RETRIEVED CONTEXT:\n{context_str}"
        )
    ])
    chain = prompt | LLM.with_structured_output(StudyResultSchema)
    study_result = chain.invoke({})
    return {"study_plan_result": study_result}

def check_plan_quality(state: StudyAgentState) -> Literal['REVISE', 'SAVE']:
    print("StudyFlow: Checking plan quality...")
    return 'SAVE'

def create_study_graph():
    workflow = StateGraph(StudyAgentState)
    workflow.add_node("retrieve", retrieve_rag_context)
    workflow.add_node("generate", generate_study_plan)
    workflow.set_entry_point("retrieve")
    workflow.add_edge("retrieve", "generate")
    workflow.add_conditional_edges("generate", check_plan_quality, {"REVISE": "generate", "SAVE": END})
    return workflow.compile()