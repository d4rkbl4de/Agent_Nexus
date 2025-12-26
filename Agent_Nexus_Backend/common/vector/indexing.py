import os
import uuid
import asyncio
from typing import List, Dict, Any, Optional, Union
from qdrant_client import AsyncQdrantClient
from qdrant_client.http import models
from common.config.logging import logger
from common.vector.embeddings import EmbeddingGenerator

class VectorIndexer:
    def __init__(
        self, 
        collection_name: str,
        vector_size: int = 1536,
        distance_metric: str = "Cosine"
    ):
        self.url = os.getenv("QDRANT_URL", "http://localhost:6333")
        self.api_key = os.getenv("QDRANT_API_KEY")
        self.collection_name = collection_name
        self.vector_size = vector_size
        self.distance = getattr(models.Distance, distance_metric.upper())
        self.client = AsyncQdrantClient(url=self.url, api_key=self.api_key)
        self.embedder = EmbeddingGenerator()

    async def _ensure_collection(self):
        try:
            collections = await self.client.get_collections()
            exists = any(c.name == self.collection_name for c in collections.collections)
            
            if not exists:
                await self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=models.VectorParams(
                        size=self.vector_size, 
                        distance=self.distance
                    )
                )
                logger.info(f"VECTOR_COLLECTION_CREATED | Name: {self.collection_name}")
        except Exception as e:
            logger.error(f"VECTOR_COLLECTION_CHECK_FAILED | Error: {str(e)}")
            raise

    async def upsert_documents(
        self, 
        texts: List[str], 
        metadata: List[Dict[str, Any]], 
        ids: Optional[List[Union[str, int]]] = None,
        trace_id: Optional[str] = None
    ) -> bool:
        t_id = trace_id or str(uuid.uuid4())
        await self._ensure_collection()
        
        try:
            embeddings = await self.embedder.generate(texts, trace_id=t_id)
            
            points = []
            for i, (text, vector) in enumerate(zip(texts, embeddings)):
                point_id = ids[i] if ids else str(uuid.uuid4())
                payload = metadata[i] if i < len(metadata) else {}
                payload["content"] = text
                
                points.append(models.PointStruct(
                    id=point_id,
                    vector=vector,
                    payload=payload
                ))

            await self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )
            
            logger.info(f"VECTOR_UPSERT_SUCCESS | Trace: {t_id} | Count: {len(points)}")
            return True
        except Exception as e:
            logger.error(f"VECTOR_UPSERT_FAILED | Trace: {t_id} | Error: {str(e)}")
            return False

    async def delete_points(self, point_ids: List[Union[str, int]]) -> bool:
        try:
            await self.client.delete(
                collection_name=self.collection_name,
                points_selector=models.PointIdsList(points=point_ids)
            )
            return True
        except Exception as e:
            logger.error(f"VECTOR_DELETE_FAILED | Error: {str(e)}")
            return False

    async def close(self):
        await self.client.close()