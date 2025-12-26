import json
import asyncio
import aiohttp
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from common.config.settings import settings
from common.config.logging import logger
from tracing.context import get_trace_id, get_agent_id, get_task_id

class TraceExporter:
    def __init__(self):
        self.queue: asyncio.Queue = asyncio.Queue(maxsize=10000)
        self.endpoint: str = settings.TRACE_EXPORTER_ENDPOINT
        self.api_key: str = settings.TRACE_EXPORTER_API_KEY
        self._worker_task: Optional[asyncio.Task] = None
        self._session: Optional[aiohttp.ClientSession] = None

    async def start(self):
        if self._worker_task is None:
            self._session = aiohttp.ClientSession(
                headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
                timeout=aiohttp.ClientTimeout(total=10)
            )
            self._worker_task = asyncio.create_task(self._flush_loop())

    async def stop(self):
        if self._worker_task:
            await self.queue.join()
            self._worker_task.cancel()
            if self._session:
                await self._session.close()

    async def export_span(
        self, 
        name: str, 
        payload: Dict[str, Any], 
        level: str = "INFO",
        metadata: Optional[Dict[str, Any]] = None
    ):
        span_data = {
            "trace_id": get_trace_id(),
            "agent_id": get_agent_id(),
            "task_id": get_task_id(),
            "span_name": name,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": level,
            "payload": payload,
            "metadata": metadata or {},
            "environment": settings.ENV
        }
        
        try:
            self.queue.put_nowait(span_data)
        except asyncio.QueueFull:
            logger.warning("Trace exporter queue full. Dropping span.")

    async def _flush_loop(self):
        batch = []
        while True:
            try:
                item = await asyncio.wait_for(self.queue.get(), timeout=settings.TRACE_FLUSH_INTERVAL)
                batch.append(item)
                
                if len(batch) >= settings.TRACE_BATCH_SIZE:
                    await self._transmit(batch)
                    batch = []
                
                self.queue.task_done()
            except asyncio.TimeoutError:
                if batch:
                    await self._transmit(batch)
                    batch = []
            except asyncio.CancelledError:
                if batch:
                    await self._transmit(batch)
                break
            except Exception as e:
                logger.error(f"Trace exporter loop error: {str(e)}")
                await asyncio.sleep(1)

    async def _transmit(self, data: List[Dict[str, Any]]):
        if not self.endpoint or not self._session:
            return

        for attempt in range(3):
            try:
                async with self._session.post(self.endpoint, json=data) as response:
                    if response.status in [200, 201, 202]:
                        return
                    logger.error(f"Trace export failed status={response.status}")
            except Exception as e:
                logger.error(f"Trace transmission error attempt={attempt}: {str(e)}")
                await asyncio.sleep(2 ** attempt)

trace_exporter = TraceExporter()