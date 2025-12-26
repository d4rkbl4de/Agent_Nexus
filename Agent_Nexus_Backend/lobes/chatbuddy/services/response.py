import uuid
import json
from typing import Any, Dict, AsyncGenerator, Optional
from datetime import datetime
from pydantic import BaseModel, Field

from common.config.logging import logger
from common.schemas.errors import AppError, ErrorCategory
from lobes.chatbuddy.agent_sdk.core.coordinator import ChatCoordinator
from lobes.chatbuddy.agent_sdk.state import chat_state_manager

class ChatStreamChunk(BaseModel):
    chunk_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    content: str
    is_final: bool = False
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class ChatResponseService:
    def __init__(self):
        self.coordinator = ChatCoordinator()

    async def generate_immediate_response(
        self,
        session_id: str,
        message: str,
        trace_id: str,
        agent_id: str
    ) -> Dict[str, Any]:
        logger.info(f"CHAT_SERVICE_IMMEDIATE | Session: {session_id} | Trace: {trace_id}")
        
        try:
            chat_state_manager.append_history(session_id, {
                "role": "user",
                "content": message,
                "trace_id": trace_id,
                "timestamp": datetime.utcnow().isoformat()
            })

            response = await self.coordinator.execute_chat_turn(
                session_id=session_id,
                message=message,
                agent_id=agent_id,
                trace_id=trace_id
            )

            chat_state_manager.append_history(session_id, {
                "role": "assistant",
                "content": response.get("content"),
                "trace_id": trace_id,
                "timestamp": datetime.utcnow().isoformat()
            })

            return {
                "session_id": session_id,
                "trace_id": trace_id,
                "response": response,
                "status": "COMPLETED"
            }

        except Exception as e:
            logger.error(f"CHAT_SERVICE_FAILURE | Session: {session_id} | Error: {str(e)}")
            raise AppError(
                category=ErrorCategory.INTERNAL,
                trace_id=trace_id,
                error={"code": "CHAT_RESPONSE_ERR", "message": "Failed to generate chat response."}
            )

    async def stream_chat_response(
        self,
        session_id: str,
        message: str,
        trace_id: str,
        agent_id: str
    ) -> AsyncGenerator[str, None]:
        logger.info(f"CHAT_SERVICE_STREAMING | Session: {session_id} | Trace: {trace_id}")
        
        full_content = []
        
        try:
            chat_state_manager.append_history(session_id, {
                "role": "user",
                "content": message,
                "trace_id": trace_id
            })

            async for chunk in self.coordinator.stream_chat_turn(
                session_id=session_id,
                message=message,
                agent_id=agent_id,
                trace_id=trace_id
            ):
                content = chunk.get("content", "")
                full_content.append(content)
                
                stream_payload = ChatStreamChunk(
                    content=content,
                    is_final=False,
                    metadata={"trace_id": trace_id}
                )
                
                yield f"data: {stream_payload.model_dump_json()}\n\n"

            final_response = "".join(full_content)
            chat_state_manager.append_history(session_id, {
                "role": "assistant",
                "content": final_response,
                "trace_id": trace_id
            })

            final_chunk = ChatStreamChunk(
                content="",
                is_final=True,
                metadata={"session_id": session_id}
            )
            yield f"data: {final_chunk.model_dump_json()}\n\n"

        except Exception as e:
            logger.error(f"STREAM_SERVICE_FAILURE | Session: {session_id} | Error: {str(e)}")
            error_payload = {
                "error": "Streaming interrupted",
                "trace_id": trace_id
            }
            yield f"data: {json.dumps(error_payload)}\n\n"

    async def get_session_context(self, session_id: str) -> Dict[str, Any]:
        state = chat_state_manager.get_state(session_id)
        return {
            "session_id": session_id,
            "history_count": len(state.history),
            "last_updated": state.updated_at.isoformat(),
            "metadata": state.values
        }