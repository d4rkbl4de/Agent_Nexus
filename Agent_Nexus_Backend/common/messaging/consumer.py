import asyncio
import json
import uuid
from typing import Any, Callable, Dict, Optional, Awaitable
from redis.exceptions import ConnectionError, TimeoutError
from common.messaging.broker import MessageBroker
from common.messaging.schemas import TaskMessage, EventMessage
from common.config.logging import logger

class MessageConsumer:
    def __init__(self, queue_name: str, trace_id: Optional[str] = None):
        self.queue_name = queue_name
        self.trace_id = trace_id or str(uuid.uuid4())
        self.broker = MessageBroker()
        self._running = False

    async def consume(self, handler: Callable[[Dict[str, Any]], Awaitable[None]]):
        self._running = True
        client = await self.broker.get_client()
        
        logger.info(f"CONSUMER_STARTED | Queue: {self.queue_name} | Trace: {self.trace_id}")
        
        while self._running:
            try:
                result = await client.brpop(self.queue_name, timeout=5)
                if result:
                    _, message_json = result
                    message_data = json.loads(message_json)
                    
                    context_trace = message_data.get("trace_id", self.trace_id)
                    
                    logger.info(f"MESSAGE_RECEIVED | Queue: {self.queue_name} | Trace: {context_trace}")
                    
                    await handler(message_data)
                    
            except (ConnectionError, TimeoutError):
                logger.warning(f"CONSUMER_CONNECTION_LOST | Retrying in 5s... | Queue: {self.queue_name}")
                await asyncio.sleep(5)
                client = await self.broker.get_client()
            except Exception as e:
                logger.error(f"CONSUMER_PROCESSING_ERROR | Queue: {self.queue_name} | Error: {str(e)}")
                continue

    async def stop(self):
        self._running = False
        logger.info(f"CONSUMER_STOP_SIGNAL_RECEIVED | Queue: {self.queue_name}")

    async def listen_for_events(self, channel_pattern: str, handler: Callable[[Dict[str, Any]], Awaitable[None]]):
        client = await self.broker.get_client()
        pubsub = client.pubsub()
        await pubsub.psubscribe(channel_pattern)
        
        logger.info(f"EVENT_LISTENER_STARTED | Pattern: {channel_pattern}")
        
        try:
            async for message in pubsub.listen():
                if message["type"] == "pmessage":
                    data = json.loads(message["data"])
                    await handler(data)
        finally:
            await pubsub.punsubscribe(channel_pattern)
            await pubsub.close()