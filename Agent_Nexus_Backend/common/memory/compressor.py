import json
from typing import List, Dict, Any, Optional
from common.ai_sdk.llm_provider import llm_provider
from common.config.logging import logger
from common.schemas.errors import AppError, ErrorCategory

class MemoryCompressor:
    def __init__(self, model_name: str = "gpt-4o-mini", token_limit: int = 1000):
        self.model_name = model_name
        self.token_limit = token_limit
        self.compression_prompt = (
            "Summarize the following conversation fragments into a dense, high-fidelity "
            "representation. Extract key entities, decisions, and unresolved tasks. "
            "Maintain technical precision while reducing word count by 70%."
        )

    async def synthesize(
        self,
        short: List[Dict[str, Any]],
        long: List[Dict[str, Any]],
        semantic: List[str],
        trace_id: Optional[str] = None
    ) -> str:
        try:
            if not any([short, long, semantic]):
                return ""

            payload = {
                "short_term_context": short[-10:],
                "historical_context": long[:5],
                "semantic_facts": semantic
            }

            raw_content = json.dumps(payload)
            
            if len(raw_content) < (self.token_limit * 3):
                return raw_content

            compressed_output = await llm_provider.generate_completion(
                model=self.model_name,
                system_prompt=self.compression_prompt,
                user_message=f"DATA_TO_COMPRESS: {raw_content}",
                temperature=0.1,
                trace_id=trace_id
            )

            return compressed_output

        except Exception as e:
            logger.error(f"MEMORY_COMPRESSION_FAILURE | Trace: {trace_id} | Error: {str(e)}")
            return json.dumps(short[-3:])

    def calculate_importance(self, content: str) -> float:
        keywords = {"decision", "update", "fixed", "error", "critical", "goal", "user_preference"}
        content_lower = content.lower()
        matches = sum(1 for word in keywords if word in content_lower)
        return min(1.0, 0.3 + (matches * 0.15))

    async def recursive_summarize(self, contents: List[str]) -> str:
        if not contents:
            return ""
        
        combined = " | ".join(contents)
        if len(combined) < self.token_limit:
            return combined
            
        return await self.synthesize([], [{"content": combined}], [])