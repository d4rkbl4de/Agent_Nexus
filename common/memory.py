from qdrant_client import QdrantClient, models
from qdrant_client.http.models import Distance, VectorParams
from common.db.vector_store import get_sync_qdrant_client
from typing import List, Dict, Any, Optional
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Assume a placeholder for the Embedder (will be replaced by actual model client later)
class PlaceholderEmbedder:
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        # Placeholder: Return random vectors of size 128
        import random
        return [[random.random() for _ in range(128)] for _ in texts]

    def embed_query(self, text: str) -> List[float]:
        # Placeholder: Return random vector of size 128
        import random
        return [random.random() for _ in range(128)]

# Configuration for the Qdrant Collection
COLLECTION_NAME = "agent_memory_v1"
VECTOR_DIMENSION = 128
DISTANCE_METRIC = Distance.COSINE

def get_qdrant_collection_client() -> QdrantClient:
    return get_sync_qdrant_client()

async def ensure_collection_exists():
    client = get_qdrant_collection_client()
    collections = client.get_collections().collections
    
    if COLLECTION_NAME not in [c.name for c in collections]:
        client.recreate_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=VECTOR_DIMENSION, distance=DISTANCE_METRIC)
        )
        print(f"Qdrant collection '{COLLECTION_NAME}' created.")
    
def chunk_and_upsert_text(text: str, source_metadata: Dict[str, Any]):
    client = get_qdrant_collection_client()
    embedder = PlaceholderEmbedder()
    
    # 1. Text Splitting (Chunker)
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, 
        chunk_overlap=200, 
        separators=["\n\n", "\n", " ", ""]
    )
    chunks = text_splitter.split_text(text)
    
    # 2. Embedding
    vectors = embedder.embed_documents(chunks)
    
    # 3. Payload and Points for Upsert
    points = []
    for i, (chunk, vector) in enumerate(zip(chunks, vectors)):
        payload = {
            "text": chunk,
            "chunk_index": i,
            **source_metadata
        }
        points.append(
            models.PointStruct(
                id=hash(f"{source_metadata.get('source_id')}-{i}"), 
                vector=vector, 
                payload=payload
            )
        )
        
    # 4. Upsert
    client.upsert(
        collection_name=COLLECTION_NAME,
        points=points,
        wait=True
    )
    print(f"Successfully upserted {len(chunks)} vectors to Qdrant.")