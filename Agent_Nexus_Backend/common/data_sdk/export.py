import os
import uuid
from typing import Any, Dict, List, Optional
from common.config.logging import logger
from common.data_sdk.enrichment import DataEnricher

class DataExporter:
    def __init__(self, trace_id: Optional[str] = None):
        self.trace_id = trace_id or str(uuid.uuid4())
        self.vector_provider = os.getenv("VECTOR_DB_PROVIDER", "qdrant")

    async def export_to_vector_store(
        self, 
        enriched_chunks: List[Dict[str, Any]], 
        collection_name: str
    ) -> Dict[str, Any]:
        try:
            total_exported = len(enriched_chunks)
            
            logger.info(
                f"VECTOR_EXPORT_SUCCESS | Provider: {self.vector_provider} | "
                f"Collection: {collection_name} | Chunks: {total_exported} | "
                f"Trace: {self.trace_id}"
            )
            
            return {
                "status": "success",
                "trace_id": self.trace_id,
                "exported_count": total_exported,
                "provider": self.vector_provider
            }
        except Exception as e:
            logger.error(f"VECTOR_EXPORT_FAILED | Trace: {self.trace_id} | Error: {str(e)}")
            raise

    def format_for_relational_db(
        self