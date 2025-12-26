import json
import uuid
from typing import Any, Dict, Optional, Union
from common.messaging.broker import MessageBroker
from common.messaging.schemas import TaskMessage, EventMessage
from common.config.logging import logger

class MessagePublisher:
    def __init__(self, trace_id: Optional[str] = None):
        self.trace_id = trace_id or str(uuid.uuid4())
        self.broker = MessageBroker()

    async def publish_task(
        self, 
        queue_name: str, 
        task_data: Union[TaskMessage, Dict[str, Any]]
    ) -> bool:
        try:
            client = await self.broker.get_client()
            
            if isinstance(task_data, TaskMessage):
                message_payload = task_data.model_dump_json()
                t_id = task_data.trace_id
            else:
                if "trace_id" not in task_data:
                    task_data["trace_id"] = self.trace_id
                message_payload = json.dumps(task_data)
                t_id = task_data["trace_id"]

            await client.lpush(queue_name, message_payload)
            
            logger.info(
                f"TASK_PUBLISHED | Queue: {queue_name} | Trace: {t_id} | "
                f"Task: {task_data.get('task_name') if isinstance(task_data, dict) else task_data.task_name}"
            )
            return True
        except Exception as e:
            logger.error(f"TASK_PUBLISH_FAILED | Queue: {queue_name} | Trace: {self.trace_id} | Error: {str(e)}")
            return False

    async def broadcast_event(
        self, 
        channel: str, 
        event_data: Union[EventMessage, Dict[str, Any]]
    ) -> int:
        try:
            client = await self.broker.get_client()
            
            if isinstance(event_data, EventMessage):
                message_payload = event_data.model_dump_json()
                t_id = event_data.trace_id
            else:
                if "trace_id" not in event_data:
                    event_data["trace_id"] = self.trace_id
                message_payload = json.dumps(event_data)
                t_id = event_data["trace_id"]

            receivers = await client.publish(channel, message_payload)
            
            logger.info(
                f"EVENT_BROADCASTED | Channel: {channel} | Trace: {t_id} | Receivers: {receivers}"
            )
            return receivers
        except Exception as e:
            logger.error(f"EVENT_BROADCAST_FAILED | Channel: {channel} | Trace: {self.trace_id} | Error: {str(e)}")
            return 0