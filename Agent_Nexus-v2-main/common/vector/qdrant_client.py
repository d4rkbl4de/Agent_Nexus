import os
from typing import List
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, PointStruct
from .search_models import VectorPoint, SearchResult


class QdrantVectorClient:
    def __init__(
        self,
        collection: str,
        url: str | None = None,
        api_key: str | None = None,
        vector_size: int = 768,
    ):
        self.collection = collection
        self.client = QdrantClient(
            url=url or os.getenv("QDRANT_URL"),
            api_key=api_key or os.getenv("QDRANT_API_KEY"),
        )
        self._ensure_collection(vector_size)

    def _ensure_collection(self, vector_size: int) -> None:
        if self.collection not in [
            c.name for c in self.client.get_collections().collections
        ]:
            self.client.create_collection(
                collection_name=self.collection,
                vectors_config=VectorParams(
                    size=vector_size,
                    distance=Distance.COSINE,
                ),
            )

    def upsert(self, points: List[VectorPoint]) -> None:
        payload = [
            PointStruct(
                id=p.id,
                vector=p.vector,
                payload=p.payload,
            )
            for p in points
        ]
        self.client.upsert(
            collection_name=self.collection,
            points=payload,
        )

    def search(
        self,
        vector: List[float],
        limit: int = 5,
    ) -> List[SearchResult]:
        results = self.client.search(
            collection_name=self.collection,
            query_vector=vector,
            limit=limit,
        )
        return [
            SearchResult(
                id=str(r.id),
                score=r.score,
                payload=r.payload or {},
            )
            for r in results
        ]
