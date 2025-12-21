import dramatiq
import httpx
import json
from dramatiq.brokers.redis import RedisBroker
from common.config import settings
from common.db import POSTGRES_CLIENT
from common.data_sdk.vector_client import VECTOR_DB_CLIENT
from common.config.logging_config import logger
from StudyFlow.utils import placeholder_utility_function

# 1. Setup the Task Broker (Redis)
try:
    broker = RedisBroker(url=settings.REDIS_URL)
    dramatiq.set_broker(broker)
    logger.info("Dramatiq broker connected to Redis.")
except Exception as e:
    logger.error(f"Failed to connect Dramatiq broker to Redis: {e}")

STUDY_FLOW_COLLECTION = "study_flow_knowledge"

@dramatiq.actor(max_retries=5)
def generate_study_plan(user_id: str, topic: str, difficulty: str, goal: str):
    """
    Asynchronously generates a personalized study plan for a user on a given topic 
    using RAG (Retrieval-Augmented Generation) and internal tools.
    """
    task_id = generate_study_plan.message_id
    logger.info(f"StudyFlow Task {task_id}: Starting study plan for user {user_id} on topic '{topic}'")
    
    # 2. RAG Step: Retrieve relevant existing knowledge chunks from Qdrant
    rag_query = f"Study material related to {topic} at {difficulty} level, focusing on {goal}"
    
    context = "No relevant context found."
    context_docs = []

    try:
        # Use the global VectorDB client (which is now correctly initialized)
        context_docs = VECTOR_DB_CLIENT.search_documents(
            collection_name=STUDY_FLOW_COLLECTION,
            query_text=rag_query,
            limit=3
        )
        context = "\n".join([doc['text'] for doc in context_docs])
        logger.info(f"StudyFlow Task {task_id}: Retrieved {len(context_docs)} context documents from Qdrant.")
        # 
    except Exception as e:
        logger.error(f"StudyFlow Task {task_id}: Failed to retrieve context from Qdrant: {e}")

    # 3. LLM Synthesis Step (Mock LLM interaction)
    
    try:
        placeholder_utility_function("Task started") 

        study_plan_result = {
            "title": f"Personalized Study Plan: {topic}",
            "difficulty": difficulty,
            "steps": [
                {"step": 1, "description": f"Master the foundational principles of {topic}."},
                {"step": 2, "description": "Review context documentation retrieved from Qdrant."},
                {"step": 3, "description": f"Complete a practical exercise based on the goal: {goal}."}
            ],
            "context_used": [doc['metadata']['source'] for doc in context_docs]
        }
        
        logger.info(f"StudyFlow Task {task_id}: Study plan object generated.")
        
    except Exception as e:
        logger.error(f"StudyFlow Task {task_id}: Failed during plan generation: {e}")
        study_plan_result = {"error": "Failed to generate plan due to a system error."}
    
    # 4. Final Output (Return structured data, not just a string)
    return {
        "task_id": task_id,
        "user_id": user_id,
        "topic": topic,
        "plan_generated_json": json.dumps(study_plan_result),
        "status": "COMPLETED"
    }