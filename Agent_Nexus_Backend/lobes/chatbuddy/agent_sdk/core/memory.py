import hashlib
from typing import List, Dict, Any, Optional
from datetime import datetime

from common.memory.facade import MemoryFacade
from common.memory.schemas import MemoryType, MemoryScope
from common.ai_sdk.embeddings import EmbeddingEngine
from common.database.vector_db import VectorClient
from common.config.logging_config import logger
from common.schemas.errors import AppError, ErrorCategory, ErrorCode

class ChatMemoryFacade:
    def __init__(self, trace_id: str, user_id: str):
        self.trace_id = trace_id
        self.user_id = user_id
        self.facade = MemoryFacade(trace_id=trace_id)
        self.vector_client = VectorClient(collection="chatbuddy_episodic")
        self.embedding_engine = EmbeddingEngine()

    async def retrieve_relevant_context(self, query: str, limit: int = 5) -> str:
        try:
            query_vector = await self.embedding_engine.get_embedding(query)
            
            filters = {
                "user_id": self.user_id,
                "memory_type": MemoryType.EPISODIC
            }
            
            results = await self.vector_client.search(
                vector=query_vector,
                filters=filters,
                limit=limit,
                min_score=0.75
            )
            
            if not results:
                return ""

            formatted_memories = []
            for res in results:
                timestamp = res.metadata.get("timestamp", "Unknown")
                content = res.payload.get("interaction_summary", "")
                formatted_memories.append(f"[{timestamp}] User: {res.payload.get('user_query')}\nAssistant: {res.payload.get('agent_response')}")

            return "\n---\n".join(formatted_memories)

        except Exception as e:
            logger.error(f"MEMORY_RETRIEVAL_ERROR | Trace: {self.trace_id} | User: {self.user_id} | Error: {str(e)}")
            return ""

    async def persist_interaction(self, user_input: str, agent_output: str):
        try:
            interaction_id = hashlib.md5(f"{self.user_id}_{datetime.utcnow().isoformat()}".encode()).hexdigest()
            
            payload = {
                "interaction_id": interaction_id,
                "user_id": self.user_id,
                "user_query": user_input,
                "agent_response": agent_output,
                "timestamp": datetime.utcnow().isoformat(),
                "memory_type": MemoryType.EPISODIC,
                "scope": MemoryScope.USER
            }

            vector = await self.embedding_engine.get_embedding(f"User: {user_input} Assistant: {agent_output}")

            await self.vector_client.upsert(
                point_id=interaction_id,
                vector=vector,
                payload=payload
            )

            await self.facade.write_intent(
                memory_type=MemoryType.EPISODIC,
                data=payload,
                importance_score=0.8
            )

        except Exception as e:
            logger.error(f"MEMORY_PERSISTENCE_ERROR | Trace: {self.trace_id} | Error: {str(e)}")

    async def get_user_preferences(self) -> Dict[str, Any]:
        return await self.facade.read_typed_memory(
            memory_type=MemoryType.SEMANTIC,
            scope=MemoryScope.USER,
            owner_id=self.user_id
        )