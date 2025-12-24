import httpx
import json
from common.config import settings
from common.config.logging_config import logger
from typing import Dict, Any

class InternalToolClient:
    """
    A client to interact with the internal specialized Lobe APIs (InsightMate, StudyFlow, ChatBuddyPlus).
    This client is the critical routing mechanism used by the AutoAgent Hub's LangGraph.
    """
    
    def __init__(self):
        self.lobe_urls: Dict[str, str] = {
            "InsightMate": settings.INSIGHT_MATE_URL,
            "StudyFlow": settings.STUDY_FLOW_URL,
            "ChatBuddyPlus": settings.CHAT_BUDDY_URL,
        }
        # Use an asynchronous client for non-blocking HTTP requests
        self.client = httpx.AsyncClient(timeout=30.0) 
        logger.info(f"InternalToolClient initialized with Lobe URLs: {self.lobe_urls}")

    def get_tool_definition(self) -> Dict[str, Any]:
        """
        Generates the LangGraph tool definitions based on the available Lobe services.
        This allows the LLM to choose the right tool/agent for execution.
        """
        return {
            "name": "call_agent_lobe",
            "description": (
                "Call a specialized agent microservice (Lobe) to execute a complex task. "
                "The available agents are InsightMate (data/analysis), StudyFlow (learning/quizzes), "
                "and ChatBuddyPlus (general chat/FAQ)."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "agent_name": {
                        "type": "string",
                        "description": "The name of the target agent to call (e.g., InsightMate, StudyFlow, ChatBuddyPlus)."
                    },
                    "user_query": {
                        "type": "string",
                        "description": "The user's original query to be passed to the specialized agent."
                    },
                    "session_id": {
                        "type": "string",
                        "description": "The unique session ID to maintain context across services."
                    },
                    "context": {
                        "type": "object",
                        "description": "Optional dictionary of previous conversation history or retrieved memory."
                    }
                },
                "required": ["agent_name", "user_query", "session_id"]
            }
        }

    async def call_agent_lobe(self, agent_name: str, user_query: str, session_id: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Executes an asynchronous HTTP POST request to the target Lobe's /process endpoint.

        This method is the actual tool function called by the LangGraph executor.
        """
        target_url = self.lobe_urls.get(agent_name)
        if not target_url:
            return {"error": f"Agent Lobe '{agent_name}' URL is not configured."}

     
        process_url = f"{target_url}/process"

        payload = {
            "user_query": user_query,
            "session_id": session_id,
            "context": context or {}
        }
            
        logger.info(f"Dispatching task to {agent_name} at {process_url}")
            
        try:
            # 
            response = await self.client.post(
                process_url,
                json=payload
            )
            response.raise_for_status()
            
            
            result = response.json()
            logger.info(f"Agent {agent_name} responded: Status={result.get('status')}, Task ID={result.get('task_id')}")

            return {
                "agent_name": agent_name,
                "status": result.get('status', 'PENDING'),
                "task_id": result.get('task_id'),
                "message": result.get('message', 'Task successfully dispatched.'),
            }
        except httpx.RequestError as e:
            error_msg = f"Failed to connect to Agent Lobe {agent_name} at {process_url}: {e}"
            logger.error(error_msg)
            return {"error": error_msg}
        except httpx.HTTPStatusError as e:
            error_msg = f"Agent Lobe {agent_name} returned error {e.response.status_code}. Detail: {e.response.text}"
            logger.error(error_msg)
            return {"error": error_msg}

INTERNAL_TOOL_CLIENT = InternalToolClient()

INTERNAL_TOOLS_MAP = {
    INTERNAL_TOOL_CLIENT.get_tool_definition()["name"]: INTERNAL_TOOL_CLIENT.call_agent_lobe,
}