from typing import List, Dict, Any, Protocol


class VectorBackend(Protocol):
    def upsert(self, vectors: List[List[float]], payloads: List[Dict[str, Any]]) -> None: ...
    def query(self, vector: List[float], top_k: int) -> List[Dict[str, Any]]: ...


class VectorClient:
    def __init__(self, backend: VectorBackend):
        self.backend = backend

    def add(self, embeddings: List[List[float]], metadatas: List[Dict[str, Any]]) -> None:
        if len(embeddings) != len(metadatas):
            raise ValueError("Embeddings and metadata size mismatch")
        self.backend.upsert(embeddings, metadatas)

    def search(self, embedding: List[float], top_k: int = 5):
        return self.backend.query(embedding, top_k)
