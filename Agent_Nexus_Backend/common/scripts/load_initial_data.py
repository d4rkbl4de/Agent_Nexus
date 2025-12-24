import os
from data_sdk import DocumentLoader, DocumentIngestor, DataPreprocessor, ChunkingStrategy, VectorClient
from memory import MemoryRecord, MemoryManager
from llm import GeminiLLM


def load_initial_data():
    data_path = os.getenv("INITIAL_DATA_PATH")
    if not data_path:
        raise RuntimeError("INITIAL_DATA_PATH not configured")

    loader = DocumentLoader()
    documents = loader.load_directory(data_path)

    preprocessor = DataPreprocessor()
    chunker = ChunkingStrategy()

    llm = GeminiLLM()

    def embed(texts):
        return [llm.model.embed_content(text).embedding for text in texts]

    vector_client = VectorClient(backend=os.getenv("VECTOR_BACKEND"))

    ingestor = DocumentIngestor(
        preprocessor=preprocessor,
        chunker=chunker,
        embedder=embed,
        vector_client=vector_client,
    )

    ingestor.ingest(documents)


if __name__ == "__main__":
    load_initial_data()
