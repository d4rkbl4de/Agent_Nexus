import json
import asyncio
from typing import AsyncGenerator, Dict, Any, List, Optional
from datetime import datetime

from common.ai_sdk.client import AgenticAISDK
from common.schemas.errors import AppError, ErrorCategory, ErrorCode
from common.config.logging_config import logger
from common.messaging.schemas import EventType, MessagePriority
from common.messaging.schemas import MessageValidator

from lobes.chatbuddy.agent_sdk.registry import ChatBuddyDefinition
from lobes.chatbuddy.agent_sdk.state import AgentStateManager, ChatState
from lobes.chatbuddy.agent_sdk.constraints import ChatBuddyConstraints
from lobes.chatbuddy.agent_sdk.core.memory import ChatMemoryFacade

class ConversationalEngine:
    def __init__(
        self,
        definition: ChatBuddyDefinition,
        state: AgentStateManager,
        constraints: ChatBuddyConstraints,
        memory: ChatMemoryFacade,
        trace_id: str,
        session_id: str
    ):
        self.definition = definition
        self.state = state
        self.constraints = constraints
        self.memory = memory
        self.trace_id = trace_id
        self.session_id = session_id
        self.ai_client = AgenticAISDK()
        self.validator = MessageValidator()

    async def chat_stream(self, user_input: str) -> AsyncGenerator[str, None]:
        self.constraints.enforce(user_input)
        
        await self.state.save_interaction(role="user", content=user_input)
        
        context_history = await self.state.get_context_window(limit=20)
        long_term_context = await self.memory.retrieve_relevant_context(user_input)
        
        system_prompt = self._construct_system_prompt(long_term_context)
        
        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(context_history)
        messages.append({"role": "user", "content": user_input})

        full_response_content = ""
        
        try:
            async for chunk in self.ai_client.stream_chat(
                model=self.definition.model_override or "gpt-4o",
                messages=messages,
                temperature=self.definition.temperature,
                max_tokens=self.definition.max_tokens,
                trace_id=self.trace_id
            ):
                if chunk:
                    full_response_content += chunk
                    yield chunk

            await self.state.save_interaction(role="assistant", content=full_response_content)
            
            asyncio.create_task(self.memory.persist_interaction(
                user_input=user_input,
                agent_output=full_response_content
            ))

        except Exception as e:
            logger.error(
                f"CONVERSATIONAL_ENGINE_FAULT | Trace: {self.trace_id}",
                trace_id=self.trace_id,
                extra={"error": str(e)}
            )
            raise AppError(
                message="Failed to generate agent response",
                category=ErrorCategory.PROVIDER_ERROR,
                code=ErrorCode.LLM_TIMEOUT,
                trace_id=self.trace_id
            )

    def _construct_system_prompt(self, long_term_context: str) -> str:
        base = self.definition.system_prompt
        if long_term_context:
            return f"{base}\n\nRELEVANT PAST CONTEXT:\n{long_term_context}\n\nUse this context to personalize your response."
        return base

    async def handle_tool_logic(self, tool_call: Dict[str, Any]):
        envelope = self.validator.create_envelope(
            source_lobe="ChatBuddy",
            trace_id=self.trace_id,
            event_type=EventType.TOOL_CALL,
            payload=tool_call,
            agent_id=self.definition.agent_id
        )

        return envelope