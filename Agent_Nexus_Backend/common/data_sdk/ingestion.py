import os
import uuid
import mimetypes
from typing import Any, Dict, List, Optional, Union, BinaryIO
from io import BytesIO
from common.config.logging import logger

class DataIngestor:
    def __init__(self, trace_id: Optional[str] = None):
        self.trace_id = trace_id or str(uuid.uuid4())
        self.supported_mimetypes = {
            "text/plain": self._ingest_text,
            "application/pdf": self._ingest_pdf,
            "text/markdown": self._ingest_text,
            "application/json": self._ingest_json
        }

    async def ingest_source(
        self, 
        source: Union[str, BytesIO, BinaryIO], 
        filename: Optional[str] = None
    ) -> Dict[str, Any]:
        try:
            content_type = self._guess_mimetype(source, filename)
            handler = self.supported_mimetypes.get(content_type, self._ingest_binary)
            
            raw_data = await handler(source)
            
            logger.info(
                f"DATA_INGESTION_SUCCESS | Trace: {self.trace_id} | Type: {content_type}"
            )
            
            return {
                "raw_content": raw_data,
                "metadata": {
                    "source_type": content_type,
                    "filename": filename,
                    "ingested_at": uuid.uuid1().hex,
                    "trace_id": self.trace_id
                }
            }
        except Exception as e:
            logger.error(f"DATA_INGESTION_FAILED | Trace: {self.trace_id} | Error: {str(e)}")
            raise

    def _guess_mimetype(self, source: Any, filename: Optional[str]) -> str:
        if filename:
            mime, _ = mimetypes.guess_type(filename)
            if mime:
                return mime
        return "application/octet-stream"

    async def _ingest_text(self, source: Any) -> str:
        if isinstance(source, (BytesIO, BinaryIO)):
            return source.read().decode("utf-8")
        if os.path.isfile(str(source)):
            with open(source, "r", encoding="utf-8") as f:
                return f.read()
        return str(source)

    async def _ingest_pdf(self, source: Any) -> str:
        import pypdf
        reader = pypdf.PdfReader(source if isinstance(source, (BytesIO, BinaryIO)) else open(source, "rb"))
        return " ".join([page.extract_text() for page in reader.pages])

    async def _ingest_json(self, source: Any) -> str:
        import json
        if isinstance(source, (BytesIO, BinaryIO)):
            return json.dumps(json.load(source))
        return json.dumps(source) if not isinstance(source, str) else source

    async def _ingest_binary(self, source: Any) -> str:
        if hasattr(source, "read"):
            return source.read().hex()
        return str(source)

class SourceValidator:
    @staticmethod
    def validate_size(source: Any, max_mb: int = 50) -> bool:
        size = 0
        if isinstance(source, (BytesIO, BinaryIO)):
            size = source.getbuffer().nbytes
        elif os.path.isfile(str(source)):
            size = os.path.getsize(source)
        
        if size > (max_mb * 1024 * 1024):
            return False
        return True