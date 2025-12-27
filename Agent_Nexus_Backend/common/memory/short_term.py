import json
from typing import List, Dict, Any, Optional
from common.config.secrets import secrets
from common.config.logging import logger
from common.schemas.errors import AppError, ErrorCategory

try:
    import redis.asyncio as redis
except ImportError:
    import redis

class ShortTermMemory:
    _redis_client: Optional[redis.Redis] = None

    def __init__(self, trace_id: str, ttl: int = 3600):
        self.trace_id = trace_id
        self.ttl = ttl
        self.key = f"stm:{self.trace_id}"
        self._ensure_client()

    def _ensure_client(self):
        if ShortTermMemory._redis_client is None:
            ShortTermMemory._redis_client = redis.from_url(
                secrets.REDIS_URL, 
                encoding="utf-8", 
                decode_responses=True
            )

    async def append(self, content: Any):
        try:
            entry = {
                "data": content,
                "timestamp": datetime.utcnow().isoformat()
            }
            serialized = json.dumps(entry)
            async with self._redis_client.pipeline(transaction=True) as pipe:
                await pipe.rpush(self.key, serialized)
                await pipe.expire(self.key, self.ttl)
                await pipe.execute()
        except Exception as e:
            logger.error(f"STM_APPEND_FAILURE | Trace: {self.trace_id} | Error: {str(e)}")

    async def get_recent(self, limit: int = 10) -> List[Dict[str, Any]]:
        try:
            raw_items = await self._redis_client.lrange(self.key, -limit, -1)
            return [json.loads(item) for item in raw_items]
        except Exception as e:
            logger.error(f"STM_RETRIEVAL_FAILURE | Trace: {self.trace_id} | Error: {str(e)}")
            return []

    async def get_full_context(self) -> List[Dict[str, Any]]:
        try:
            raw_items = await self._redis_client.lrange(self.key, 0, -1)
            return [json.loads(item) for item in raw_items]
        except Exception as e:
            logger.error(f"STM_FULL_RETRIEVAL_FAILURE | Trace: {self.trace_id} | Error: {str(e)}")
            return []

    async def clear(self) -> bool:
        try:
            await self._redis_client.delete(self.key)
            return True
        except Exception as e:
            logger.error(f"STM_CLEAR_FAILURE | Trace: {self.trace_id} | Error: {str(e)}")
            return False

    async def update_last_entry(self, updated_content: Any):
        try:
            async with self._redis_client.pipeline(transaction=True) as pipe:
                await pipe.lpop(self.key, count=-1)
                entry = {
                    "data": updated_content,
                    "timestamp": datetime.utcnow().isoformat()
                }
                await pipe.rpush(self.key, json.dumps(entry))
                await pipe.execute()
        except Exception as e:
            logger.error(f"STM_UPDATE_FAILURE | Trace: {self.trace_id} | Error: {str(e)}")

    @classmethod
    async def close_connection(cls):
        if cls._redis_client:
            await cls._redis_client.close()