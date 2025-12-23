from typing import List
import redis
import json
from .history_model import MemoryRecord


class RedisMemoryBackend:
    def __init__(self, url: str, namespace: str = "memory"):
        self.client = redis.from_url(url, decode_responses=True)
        self.namespace = namespace

    def _key(self, agent_id: str) -> str:
        return f"{self.namespace}:{agent_id}"

    def append(self, record: MemoryRecord, ttl: int | None = None) -> None:
        key = self._key(record.agent_id)
        payload = json.dumps(record.__dict__, default=str)
        self.client.rpush(key, payload)
        if ttl:
            self.client.expire(key, ttl)

    def fetch(self, agent_id: str, limit: int | None = None) -> List[MemoryRecord]:
        key = self._key(agent_id)
        raw = self.client.lrange(key, -limit if limit else 0, -1)
        records = []
        for item in raw:
            data = json.loads(item)
            records.append(MemoryRecord(**data))
        return records

    def clear(self, agent_id: str) -> None:
        self.client.delete(self._key(agent_id))
