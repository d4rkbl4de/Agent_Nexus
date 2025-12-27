from typing import List, Dict, Any, Optional
from common.vector.embeddings import EmbeddingGenerator
from common.vector.indexing import VectorIndexer
from common.vector.search import VectorSearcher
from common.vector.ranking import ResultRanker

class VectorManifest:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(VectorManifest, cls).__new__(cls)
            cls._instance.embeddings = EmbeddingGenerator()
            cls._instance.indexer = VectorIndexer()
            cls._instance.searcher = VectorSearcher()
            cls._instance.ranker = ResultRanker()
        return cls._instance

    async def semantic_retrieval(
        self, 
        query: str, 
        collection: str, 
        top_k: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        query_vector = await self.embeddings.generate(query)
        raw_results = await self.searcher.query(
            vector=query_vector,
            collection=collection,
            limit=top_k * 2,
            filters=filters
        )
        ranked_results = self.ranker.rerank(query, raw_results)
        return ranked_results[:top_k]

vector_manifest = VectorManifest()

__all__ = [
    "vector_manifest",
    "EmbeddingGenerator",
    "VectorIndexer",
    "VectorSearcher",
    "ResultRanker"
]