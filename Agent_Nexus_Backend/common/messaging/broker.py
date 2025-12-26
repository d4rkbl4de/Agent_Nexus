import os
import asyncio
import redis.asyncio as redis
from typing import Optional, Any
from redis.asyncio.retry import Retry
from redis.backoff import ExponentialBackoff
from redis.exceptions import ConnectionError, TimeoutError
from common.config.logging import logger

class MessageBroker:
    _instance: Optional['MessageBroker'] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MessageBroker, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        
        self.host = os.getenv("REDIS_HOST", "localhost")
        self.port = int(os.getenv("REDIS_PORT", 6379))
        self.db = int(os.getenv("REDIS_DB", 0))
        self.password = os.getenv("REDIS_PASSWORD", None)
        self.max_connections = int(os.getenv("REDIS_MAX_CONNECTIONS", 100))
        self.socket_timeout = int(os.getenv("REDIS_TIMEOUT", 5))
        
        self._pool: Optional[redis.ConnectionPool] = None
        self._client: Optional[redis.Redis] = None
        self._initialized = True

    async def connect(self) -> redis.Redis:
        if self._client:
            return self._client

        retry = Retry(ExponentialBackoff(cap=10, base=1), 3)
        
        self._pool = redis.ConnectionPool(
            host=self.host,
            port=self.port,
            db=self.db,
            password=self.password,
            max_connections=self.max_connections,
            socket_timeout=self.socket_timeout,
            retry_on_timeout=True,
            health_check_interval=30,
            decode_responses=True
        )
        
        self._client = redis.Redis(connection_pool=self._pool, retry=retry)
        
        try:
            await self._client.ping()
            logger.info(f"BROKER_CONNECTION_ESTABLISHED | {self.host}:{self.port}/{self.db}")
            return self._client
        except (ConnectionError, TimeoutError) as e:
            logger.critical(f"BROKER_CONNECTION_FAILED | {str(e)}")
            await self.disconnect()
            raise

    async def get_client(self) -> redis.Redis:
        if not self._client:
            return await self.connect()
        return self._client

    async def disconnect(self):
        if self._client:
            await self._client.close()
            self._client = None
        if self._pool:
            await self._pool.disconnect()
            self._pool = None
        logger.info("BROKER_RESOURCES_RELEASED")

    async def check_health(self) -> bool:
        try:
            client = await self.get_client()
            return await client.ping()
        except Exception:
            return False

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.disconnect()