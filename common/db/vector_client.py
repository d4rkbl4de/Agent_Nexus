import uuid
from typing import Any, Dict, List, Optional
from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.exceptions import UnexpectedResponse
from .exceptions import DatabaseError, CollectionNotFoundError, VectorDimensionMismatchError

class VectorClient:
    def __init__(
        self, 
        host: str = "localhost", 
        port: int = 6333, 
        api_key: Optional[str] = None
    ):
        try:
            self.client = QdrantClient(host=host, port=port, api_key=api_key)
        except Exception as e:
            raise DatabaseError(f"Failed to connect to Vector DB: {e}")

    def _ensure_collection(self, collection_name: str, vector_size: int):
        try:
            collections = self.client.get_collections().collections
            exists = any(c.name == collection_name for c in collections)
            
            if not exists:
                self.client.create_collection(
                    collection_name=collection_name,
                    vectors_config=models.VectorParams(
                        size=vector_size, 
                        distance=models.Distance.COSINE
                    ),
                )
        except Exception as e:
            raise DatabaseError(f"Vector collection management failed: {e}")

    async def upsert(
        self, 
        collection_name: str, 
        vectors: List[List[float]], 
        payloads: List[Dict[str, Any]]
    ) -> List[str]:
        if not vectors:
            return []
            
        self._ensure_collection(collection_name, len(vectors[0]))
        
        ids = [str(uuid.uuid4()) for _ in range(len(vectors))]
        
        points = [
            models.PointStruct(
                id=idx,
                vector=vector,
                payload=payload
            )
            for idx, vector, payload in zip(ids, vectors, payloads)
        ]

        try:
            self.client.upsert(
                collection_name=collection_name,
                points=points
            )
            return ids
        except Exception as e:
            raise DatabaseError(f"Vector upsert failed: {e}")

    async def search(
        self, 
        collection_name: str, 
        query_vector: List[float], 
        limit: int = 5,
        score_threshold: float = 0.35
    ) -> List[Dict[str, Any]]:
        try:
            results = self.client.search(
                collection_name=collection_name,
                query_vector=query_vector,
                limit=limit,
                score_threshold=score_threshold,
                with_payload=True
            )
            return [hit.payload for hit in results if hit.payload]
        except UnexpectedResponse as e:
            if "not found" in str(e).lower():
                raise CollectionNotFoundError(f"Collection {collection_name} does not exist")
            raise DatabaseError(f"Vector search failed: {e}")
        except Exception as e:
            raise DatabaseError(f"Vector search failed: {e}")

    async def delete_points(self, collection_name: str, point_ids: List[str]):
        try:
            self.client.delete(
                collection_name=collection_name,
                points_selector=models.PointIdsList(points=point_ids)
            )
        except Exception as e:
            raise DatabaseError(f"Failed to delete points: {e}")