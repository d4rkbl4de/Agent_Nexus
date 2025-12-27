import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime
from common.ai_sdk.llm_provider import llm_provider
from common.config.logging import logger
from common.schemas.errors import AppError, ErrorCategory

class LongTermMemory:
    def __init__(self, agent_id: str, collection_name: str = "agent_knowledge"):
        self.agent_id = agent_id
        self.collection_name = collection_name
        self.vector_db = None 

    async def _get_embedding(self, text: str) -> List[float]:
        try:
            return await llm_provider.get_embeddings(text)
        except Exception as e:
            logger.error(f"EMBEDDING_GENERATION_FAILED | Agent: {self.agent_id} | Error: {str(e)}")
            raise AppError(
                message="Failed to generate vector embeddings for long-term memory",
                category=ErrorCategory.INTERNAL_ERROR,
                status_code=500
            )

    async def store(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        doc_id = str(uuid.uuid4())
        embedding = await self._get_embedding(content)
        
        extended_metadata = {
            **(metadata or {}),
            "agent_id": self.agent_id,
            "created_at": datetime.utcnow().isoformat(),
            "content_hash": hash(content)
        }

        try:
            from common.db.vector_client import vector_client
            await vector_client.upsert(
                collection=self.collection_name,
                points=[{
                    "id": doc_id,
                    "vector": embedding,
                    "payload": {
                        "content": content,
                        "metadata": extended_metadata
                    }
                }]
            )
            return doc_id
        except Exception as e:
            logger.error(f"VECTOR_STORE_FAILURE | Agent: {self.agent_id} | Error: {str(e)}")
            return ""

    async def search(self, query: str, limit: int = 5, min_score: float = 0.7) -> List[Dict[str, Any]]:
        try:
            query_vector = await self._get_embedding(query)
            from common.db.vector_client import vector_client
            
            results = await vector_client.search(
                collection=self.collection_name,
                query_vector=query_vector,
                query_filter={
                    "must": [
                        {"key": "metadata.agent_id", "match": {"value": self.agent_id}}
                    ]
                },
                limit=limit,
                score_threshold=min_score
            )

            return [
                {
                    "content": res.payload["content"],
                    "metadata": res.payload["metadata"],
                    "score": res.score
                }
                for res in results
            ]
        except Exception as e:
            logger.warning(f"VECTOR_SEARCH_FALLBACK | Agent: {self.agent_id} | Error: {str(e)}")
            return []

    async def batch_store(self, items: List[Dict[str, Any]]):
        for item in items:
            await self.store(item["content"], item.get("metadata"))

    async def delete_by_filter(self, filter_criteria: Dict[str, Any]):
        from common.db.vector_client import vector_client
        await vector_client.delete(
            collection=self.collection_name,
            filter_criteria={
                "must": [
                    {"key": "metadata.agent_id", "match": {"value": self.agent_id}},
                    *[{"key": f"metadata.{k}", "match": {"value": v}} for k, v in filter_criteria.items()]
                ]
            }
        )