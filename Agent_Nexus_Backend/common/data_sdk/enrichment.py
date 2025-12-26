import uuid
from typing import Any, Dict, List, Optional
from datetime import datetime
from common.config.logging import logger

class DataEnricher:
    def __init__(self, trace_id: Optional[str] = None):
        self.trace_id = trace_id or str(uuid.uuid4())

    def add_contextual_metadata(
        self, 
        chunks: List[Dict[str, Any]], 
        source_metadata: Dict[str, Any],
        agent_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        enriched_chunks = []
        
        for index, chunk in enumerate(chunks):
            enriched_payload = {
                "content": chunk.get("content"),
                "metadata": {
                    **chunk.get("metadata", {}),
                    **source_metadata,
                    "chunk_index": index,
                    "total_chunks": len(chunks),
                    "trace_id": self.trace_id,
                    "agent_id": agent_id,
                    "enriched_at": datetime.utcnow().isoformat(),
                    "version": "v1"
                }
            }
            enriched_chunks.append(enriched_payload)
            
        logger.info(f"DATA_ENRICHMENT_COMPLETE | Trace: {self.trace_id} | Chunks: {len(enriched_chunks)}")
        return enriched_chunks

    def inject_semantic_labels(
        self, 
        chunks: List[Dict[str, Any]], 
        labels: List[str]
    ) -> List[Dict[str, Any]]:
        for chunk in chunks:
            chunk["metadata"]["semantic_labels"] = labels
            chunk["metadata"]["memory_type"] = "semantic" # Rule 15
        return chunks

    def link_episodic_context(
        self, 
        chunks: List[Dict[str, Any]], 
        event_id: str, 
        timestamp: str
    ) -> List[Dict[str, Any]]:
        for chunk in chunks:
            chunk["metadata"]["event_id"] = event_id
            chunk["metadata"]["event_timestamp"] = timestamp
            chunk["metadata"]["memory_type"] = "episodic" # Rule 15
        return chunks