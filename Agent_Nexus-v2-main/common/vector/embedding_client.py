from typing import List, Protocol


class EmbeddingBackend(Protocol):
    def embed(self, texts: List[str]) -> List[List[float]]: ...


class EmbeddingClient:
    def __init__(self, backend: EmbeddingBackend):
        self.backend = backend

    def embed(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            raise ValueError("No texts provided for embedding")
        embeddings = self.backend.embed(texts)
        if len(embeddings) != len(texts):
            raise RuntimeError("Embedding size mismatch")
        return embeddings
