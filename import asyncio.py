import asyncio
import os
from common.memory import ensure_collection_exists, chunk_and_upsert_text, COLLECTION_NAME
from common.db.vector_store import get_sync_qdrant_client

async def main():
    await ensure_collection_exists()

    sample_text = (
        "Project Hydra kick-off notes. Discussion focused on three core areas: "
        "API Standardization, Async Task Queue implementation, and Vector Store usage for RAG. "
        "Action Item: Farhan to finalize the Pydantic schemas by end of week. "
        "The team agreed to use Redis for the async queue and Qdrant for the vector store. "
        "A follow-up is scheduled for next Tuesday to review the LangChain agent scaffolding."
    )
    
    metadata = {
        "source": "InsightMate",
        "source_id": 99,
        "document_type": "meeting_summary"
    }

    chunk_and_upsert_text(sample_text, metadata)
    
    client = get_sync_qdrant_client()
    count = client.count(collection_name=COLLECTION_NAME, exact=True).count
    print(f"\nVerification: Total vectors in collection '{COLLECTION_NAME}': {count}")
    
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except RuntimeError as e:
        if "cannot run" in str(e):
             import nest_asyncio
             nest_asyncio.apply()
             asyncio.run(main())
        else:
             raise e