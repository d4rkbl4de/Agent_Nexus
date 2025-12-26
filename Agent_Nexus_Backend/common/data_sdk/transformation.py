import uuid
import re
from typing import Any, Dict, List, Optional
from common.config.logging import logger

class DataTransformer:
    def __init__(self, trace_id: Optional[str] = None):
        self.trace_id = trace_id or str(uuid.uuid4())

    async def chunk_text(
        self, 
        text: str, 
        chunk_size: int = 1000, 
        chunk_overlap: int = 200,
        strategy: str = "recursive"
    ) -> List[Dict[str, Any]]:
        try:
            if strategy == "recursive":
                chunks = self._recursive_split(text, chunk_size, chunk_overlap)
            else:
                chunks = self._simple_split(text, chunk_size, chunk_overlap)

            transformed_data = [
                {
                    "content": chunk,
                    "metadata": {
                        "chunk_size": len(chunk),
                        "strategy": strategy,
                        "trace_id": self.trace_id
                    }
                }
                for chunk in chunks
            ]

            logger.info(f"TRANSFORMATION_CHUNK_SUCCESS | Trace: {self.trace_id} | Chunks: {len(transformed_data)}")
            return transformed_data
        except Exception as e:
            logger.error(f"TRANSFORMATION_CHUNK_FAILED | Trace: {self.trace_id} | Error: {str(e)}")
            raise

    def _recursive_split(self, text: str, chunk_size: int, chunk_overlap: int) -> List[str]:
        separators = ["\n\n", "\n", " ", ""]
        
        def split_text(txt: str, seps: List[str]):
            if len(txt) <= chunk_size:
                return [txt]
            
            separator = seps[0] if seps else ""
            parts = txt.split(separator) if separator else list(txt)

            current_chunk = ""
            results = []
            
            for part in parts:
                if len(current_chunk) + len(part) + (len(separator) if current_chunk else 0) <= chunk_size:
                    current_chunk += (separator if current_chunk else "") + part
                else:
                    if current_chunk:
                        results.append(current_chunk)
                    
                    if len(part) > chunk_size:
                        results.extend(split_text(part, seps[1:] if len(seps) > 1 else []))
                        current_chunk = ""
                    else:
                        current_chunk = part
            
            if current_chunk:
                results.append(current_chunk)
            return results

        raw_chunks = split_text(text, separators)
        
        if chunk_overlap > 0 and len(raw_chunks) > 1:
            overlapped_chunks = []
            for i in range(len(raw_chunks)):
                if i == 0:
                    overlapped_chunks.append(raw_chunks[i])
                    continue
                
                overlap_prefix = raw_chunks[i-1][-chunk_overlap:]
                overlapped_chunks.append(overlap_prefix + raw_chunks[i])
            return overlapped_chunks
            
        return raw_chunks

    def _simple_split(self, text: str, chunk_size: int, chunk_overlap: int) -> List[str]:
        chunks = []
        step = chunk_size - chunk_overlap
        for i in range(0, len(text), step if step > 0 else chunk_size):
            chunks.append(text[i:i + chunk_size])
        return chunks

    def clean_content(self, text: str) -> str:
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'[^\x00-\x7F]+', '', text)
        return text.strip()

    async def generate_embedding_proxy(self, chunks: List[Dict[str, Any]], model: str = "text-embedding-3-small") -> List[Dict[str, Any]]:
        for chunk in chunks:
            chunk["metadata"]["embedding_model"] = model
            chunk["embedding_reserved"] = True 
        return chunks