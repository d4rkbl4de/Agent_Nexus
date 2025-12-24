from typing import List, Callable
from .document_model import Document
from .data_preprocessor import DataPreprocessor
from .chunking_strategy import ChunkingStrategy
from .vector_client import VectorClient


class DocumentIngestor:
    def __init__(
        self,
        preprocessor: DataPreprocessor,
        chunker: ChunkingStrategy,
        embedder: Callable[[List[str]], List[List[float]]],
        vector_client: VectorClient,
    ):
        self.preprocessor = preprocessor
        self.chunker = chunker
        self.embedder = embedder
        self.vector_client = vector_client

    def ingest(self, documents: List[Document]) -> None:
        all_chunks = []
        all_metadata = []

        for doc in documents:
            processed = self.preprocessor.process(doc.content)
            chunks = self.chunker.chunk(processed)
            for idx, chunk in enumerate(chunks):
                all_chunks.append(chunk)
                all_metadata.append(
                    {
                        "document_id": doc.id,
                        "chunk_index": idx,
                        **doc.metadata,
                    }
                )

        embeddings = self.embedder(all_chunks)
        self.vector_client.add(embeddings, all_metadata)
