import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

from common.config.logging_config import logger
from common.schemas.errors import AppError, ErrorCategory, ErrorCode
from common.messaging.schemas import EventType
from common.messaging.mediator import mediator
from lobes.insightmate.agent_sdk.core.executor import InsightExecutor

class TaskDefinition(BaseModel):
    task_id: str
    name: str
    description: str
    required_inputs: List[str]
    timeout_seconds: int = 300
    retry_policy: Dict[str, Any] = Field(default_factory=lambda: {"max_retries": 3, "backoff": "exponential"})

class InsightTaskRegistry:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(InsightTaskRegistry, cls).__new__(cls)
            cls._instance._tasks: Dict[str, TaskDefinition] = {}
            cls._instance._load_static_tasks()
        return cls._instance

    def _load_static_tasks(self):
        tasks = [
            TaskDefinition(
                task_id="extract_action_items",
                name="Action Item Extractor",
                description="Identifies specific tasks and owners from meeting transcripts",
                required_inputs=["transcript", "participants"]
            ),
            TaskDefinition(
                task_id="generate_meeting_summary",
                name="Executive Summarizer",
                description="Creates a high-level summary of meeting discussions",
                required_inputs=["transcript"]
            ),
            TaskDefinition(
                task_id="detect_sentiment_trends",
                name="Meeting Sentiment Analyzer",
                description="Tracks emotional shifts throughout the discussion",
                required_inputs=["transcript"]
            )
        ]
        for task in tasks:
            self._tasks[task.task_id] = task

    def get_task(self, task_id: str) -> TaskDefinition:
        task = self._tasks.get(task_id)
        if not task:
            raise AppError(
                message=f"Task {task_id} not registered in InsightMate",
                category=ErrorCategory.NOT_FOUND_ERROR,
                code=ErrorCode.RESOURCE_NOT_FOUND
            )
        return task

    def list_tasks(self) -> List[TaskDefinition]:
        return list(self._tasks.values())

class InsightTaskWorker:
    def __init__(self, trace_id: str):
        self.trace_id = trace_id
        self.executor = InsightExecutor(trace_id=trace_id)

    async def execute(self, task_id: str, inputs: Dict[str, Any]) -> Dict[str, Any]:
        task_def = task_registry.get_task(task_id)
        
        for input_key in task_def.required_inputs:
            if input_key not in inputs:
                raise AppError(
                    message=f"Missing required input: {input_key}",
                    category=ErrorCategory.VALIDATION_ERROR,
                    code=ErrorCode.BAD_REQUEST,
                    trace_id=self.trace_id
                )

        logger.info(
            f"TASK_EXECUTION_START | Task: {task_id}",
            trace_id=self.trace_id,
            lobe="InsightMate"
        )

        try:
            result = await asyncio.wait_for(
                self.executor.run_specific_task(task_id, inputs),
                timeout=task_def.timeout_seconds
            )

            await mediator.publish(
                event_type=EventType.TASK_COMPLETED,
                payload={"task_id": task_id, "result": result},
                trace_id=self.trace_id
            )

            return result

        except asyncio.TimeoutError:
            raise AppError(
                message=f"Task {task_id} timed out after {task_def.timeout_seconds}s",
                category=ErrorCategory.INTERNAL_ERROR,
                code=ErrorCode.LLM_TIMEOUT,
                trace_id=self.trace_id
            )
        except Exception as e:
            logger.error(f"TASK_EXECUTION_FAILED | {str(e)}", trace_id=self.trace_id)
            raise

task_registry = InsightTaskRegistry()