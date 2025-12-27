import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime
from common.ai_sdk.llm_provider import llm_provider
from common.config.logging import logger
from common.schemas.errors import AppError, ErrorCategory

class SemanticMemory:
    def __init__(self, collection_name: str = "global_semantic_knowledge"):
        self.collection_name = collection_name
        self.namespace = "shared_facts"

    async def _get_embedding(self, text: str) -> List[float]:
        try:
            return await llm_provider.get_embeddings(text)
        except Exception as e:
            logger.error(f"SEMANTIC_EMBEDDING_ERROR | Error: {str(e)}")
            raise AppError(
                message="Failed to generate embeddings for semantic lookup",
                category=ErrorCategory.INTERNAL_ERROR,
                status_code=500
            )

    async def query(self, concept: str, limit: int = 3) -> List[str]:
        try:
            query_vector = await self._get_embedding(concept)
            from common.db.vector_client import vector_client
            
            results = await vector_client.search(
                collection=self.collection_name,
                query_vector=query_vector,
                query_filter={
                    "must": [
                        {"key": "metadata.namespace", "match": {"value": self.namespace}}
                    ]
                },
                limit=limit,
                score_threshold=0.85
            )

            return [res.payload["fact"] for res in results]
        except Exception as e:
            logger.warning(f"SEMANTIC_QUERY_BYPASS | Reason: {str(e)}")
            return []

    async def anchor_fact(self, fact: str, metadata: Optional[Dict[str, Any]] = None):
        fact_id = str(uuid.uuid4())
        embedding = await self._get_embedding(fact)
        
        payload = {
            "fact": fact,
            "metadata": {
                **(metadata or {}),
                "namespace": self.namespace,
                "created_at": datetime.utcnow().isoformat(),
                "is_verified": True
            }
        }

        try:
            from common.db.vector_client import vector_client
            await vector_client.upsert(
                collection=self.collection_name,
                points=[{
                    "id": fact_id,
                    "vector": embedding,
                    "payload": payload
                }]
            )
            return fact_id
        except Exception as e:
            logger.error(f"SEMANTIC_ANCHOR_FAILURE | Fact: {fact[:50]} | Error: {str(e)}")
            return None

    async def get_related_concepts(self, concepts: List[str]) -> List[str]:
        results = []
        for concept in concepts:
            facts = await self.query(concept, limit=2)
            results.extend(facts)
        return list(set(results))