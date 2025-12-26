import uuid
from typing import List, Dict, Any, Optional
from common.config.logging import logger

class ResultRanker:
    def __init__(self, trace_id: Optional[str] = None):
        self.trace_id = trace_id or str(uuid.uuid4())

    def rerank_by_recency(
        self, 
        results: List[Dict[str, Any]], 
        timestamp_key: str = "created_at",
        weight: float = 0.3
    ) -> List[Dict[str, Any]]:
        try:
            if not results:
                return []

            ranked_results = sorted(
                results,
                key=lambda x: (x.get("score", 0) * (1 - weight)) + 
                              (float(x.get("payload", {}).get(timestamp_key, 0)) * weight),
                reverse=True
            )
            
            logger.info(f"RANKING_RECENCY_APPLIED | Trace: {self.trace_id} | Count: {len(results)}")
            return ranked_results
        except Exception as e:
            logger.error(f"RANKING_RECENCY_FAILED | Trace: {self.trace_id} | Error: {str(e)}")
            return results

    def apply_threshold(
        self, 
        results: List[Dict[str, Any]], 
        threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        filtered = [r for r in results if r.get("score", 0) >= threshold]
        logger.info(f"RANKING_THRESHOLD_FILTER | Trace: {self.trace_id} | Before: {len(results)} | After: {len(filtered)}")
        return filtered

    def reciprocal_rank_fusion(
        self, 
        vector_results: List[Dict[str, Any]], 
        keyword_results: List[Dict[str, Any]], 
        k: int = 60
    ) -> List[Dict[str, Any]]:
        scores: Dict[str, float] = {}
        
        for rank, res in enumerate(vector_results):
            doc_id = str(res.get("id"))
            scores[doc_id] = scores.get(doc_id, 0) + 1 / (rank + k)
            
        for rank, res in enumerate(keyword_results):
            doc_id = str(res.get("id"))
            scores[doc_id] = scores.get(doc_id, 0) + 1 / (rank + k)
            
        combined = []
        lookup = {str(r.get("id")): r for r in vector_results + keyword_results}
        
        sorted_ids = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        
        for doc_id, score in sorted_ids:
            original_doc = lookup[doc_id]
            original_doc["rrf_score"] = score
            combined.append(original_doc)
            
        logger.info(f"RANKING_RRF_COMPLETE | Trace: {self.trace_id} | Total Unique: {len(combined)}")
        return combined

    def diversity_filter(
        self, 
        results: List[Dict[str, Any]], 
        metadata_key: str, 
        max_per_category: int = 2
    ) -> List[Dict[str, Any]]:
        counts: Dict[str, int] = {}
        diverse_results = []
        
        for res in results:
            category = res.get("payload", {}).get(metadata_key, "unknown")
            if counts.get(category, 0) < max_per_category:
                diverse_results.append(res)
                counts[category] = counts.get(category, 0) + 1
                
        return diverse_results