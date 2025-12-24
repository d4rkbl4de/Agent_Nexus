import os
import logging
import dramatiq
from dramatiq.brokers.redis import RedisBroker
import httpx
from typing import Dict, Any
from utils import call_gemini_api

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

REDIS_URL = os.getenv("REDIS_URL")
INSIGHT_MATE_URL = os.getenv("INSIGHT_MATE_URL")
STUDY_FLOW_URL = os.getenv("STUDY_FLOW_URL")
CHAT_BUDDY_URL = os.getenv("CHAT_BUDDY_URL")

if not REDIS_URL:
    logger.error("REDIS_URL is not set. Dramatiq will use the synchronous default.")
    broker = dramatiq.get_broker()
else:
    broker = RedisBroker(url=REDIS_URL)

dramatiq.set_broker(broker)


def determine_target_agent(query: str) -> str:
    query_lower = query.lower()
    
    if "data" in query_lower or "analysis" in query_lower or "report" in query_lower or "metric" in query_lower:
        return "InsightMate"
    elif "learn" in query_lower or "study" in query_lower or "summary" in query_lower or "concept" in query_lower:
        return "StudyFlow"
    elif "chat" in query_lower or "general question" in query_lower or "casual" in query_lower:
        return "ChatBuddyPlus"
    else:
        return "ChatBuddyPlus"


def get_target_url(agent_name: str) -> str:
    if agent_name == "InsightMate":
        return INSIGHT_MATE_URL
    elif agent_name == "StudyFlow":
        return STUDY_FLOW_URL
    elif agent_name == "ChatBuddyPlus":
        return CHAT_BUDDY_URL
    return ""


@dramatiq.actor(max_retries=3)
def hub_orchestrate_task(user_query: str, session_id: str, context: Dict[str, Any]):
    logger.info(f"Worker received query for session {session_id}: {user_query}")
    
    target_agent = determine_target_agent(user_query)
    target_url = get_target_url(target_agent)

    if not target_url:
        logger.error(f"Cannot orchestrate: URL for {target_agent} is missing.")
        return

    logger.info(f"Target Agent: {target_agent} at {target_url}/process")

    try:
        with httpx.Client(base_url=target_url, timeout=30) as client:
            payload = {
                "user_query": user_query,
                "session_id": session_id,
                "context": context
            }
            response = client.post("/process", json=payload)
            response.raise_for_status()
            
            final_result = response.json().get('result', f"Agent {target_agent} processed but returned no result.")
            
            logger.info(f"Successfully processed by {target_agent}. Result snippet: {final_result[:50]}...")
            
    except httpx.HTTPStatusError as e:
        error_detail = f"Agent API call failed for {target_agent} with status {e.response.status_code}. Response: {e.response.text}"
        logger.error(error_detail)
        raise
    except httpx.RequestError as e:
        error_detail = f"Network or request error when calling {target_agent}: {e}"
        logger.error(error_detail)
        raise