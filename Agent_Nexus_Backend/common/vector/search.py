import os
import uuid
from typing import List, Dict, Any, Optional, Union
from qdrant_client import AsyncQdrantClient
from qdrant_client.http import models
from common.config.logging import logger
from common.vector.embeddings import EmbeddingGenerator
from common.vector.ranking import ResultRanker

class VectorSearcher:
    def __init__(self, collection_name: str):
        self.url = os.getenv("QDRANT_URL", "http://localhost:6333")
        self.api_key = os.getenv("QDRANT_API_KEY")
        self.collection_name = collection_name
        self.client = AsyncQdrantClient(url=self.url, api_key=self.api_key)
        self.embedder = EmbeddingGenerator()
        self.ranker = ResultRanker()

    async def search(
        self,
        query: str,
        limit: int = 10,
        score_threshold: float = 0.35,
        filters: Optional[Dict[str, Any]] = None,
        trace_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        t_id = trace_id or str(uuid.uuid4())
        
        try:
            query_vector = await self.embedder.generate_single(query, trace_id=t_id)
            
            qdrant_filter = None
            if filters:
                conditions = [
                    models.FieldCondition(key=k, match=models.MatchValue(value=v))
                    for k, v in filters.items()
                ]
                qdrant_filter = models.Filter(must=conditions)

            search_result = await self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                query_filter=qdrant_filter,
                limit=limit,
                score_threshold=score_threshold,
                with_payload=True,
                with_vectors=False
            )

            results = [
                {
                    "id": hit.id,
                    "score": hit.score,
                    "payload": hit.payload,
                    "trace_id": t_id
                }
                for hit in search_result
            ]

            logger.info(f"VECTOR_SEARCH_SUCCESS | Trace: {t_id} | Hits: {len(results)}")
            return results

        except Exception as e:
            logger.error(f"VECTOR_SEARCH_FAILED | Trace: {t_id} | Error: {str(e)}")
            return []

    async def hybrid_search(
        self,
        query: str,
        limit: int = 10,
        trace_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        t_id = trace_id or str(uuid.uuid4())
        
        vector_results = await self.search(query, limit=limit * 2, trace_id=t_id)
        
        try:
            scroll_result = await self.client.scroll(
                collection_name=self.collection_name,
                scroll_filter=models.Filter(
                    must=[models.FieldCondition(key="content", match=models.MatchText(text=query))]
                ),
                limit=limit * 2,
                with_payload=True
            )
            
            keyword_results = [
                {"id": hit.id, "payload": hit.payload, "score": 1.0} 
                for hit in scroll_result[0]
            ]
            
            final_results = self.ranker.reciprocal_rank_fusion(
                vector_results, 
                keyword_results
            )
            
            return final_results[:limit]
            
        except Exception as e:
            logger.warning(f"HYBRID_FALLBACK_TO_VECTOR | Trace: {t_id} | Reason: {str(e)}")
            return vector_results[:limit]

    async def close(self):
        await self.client.close()