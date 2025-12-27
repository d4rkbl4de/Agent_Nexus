import asyncio
from typing import Dict, Any
from common.messaging.mediator import mediator
from common.messaging.schemas import EventType
from common.config.logging_config import logger
from lobes.studyflow.agent_sdk import study_sdk
from lobes.studyflow.tasks import study_task_registry

class StudyFlowApplication:
    def __init__(self):
        self.lobe_name = "StudyFlow"
        self.is_running = False

    async def start(self):
        if self.is_running:
            return
        
        await self._setup_event_subscriptions()
        await self._warm_up_sdk()
        
        self.is_running = True
        logger.info(f"LOBE_START_SUCCESS | {self.lobe_name}", trace_id="SYSTEM_BOOT")

    async def stop(self):
        self.is_running = False
        await study_task_registry.cleanup_active_sessions()
        logger.info(f"LOBE_STOP_SUCCESS | {self.lobe_name}", trace_id="SYSTEM_BOOT")

    async def _setup_event_subscriptions(self):
        await mediator.subscribe(EventType.USER_CREATED, self.handle_user_initialization)
        await mediator.subscribe(EventType.DATA_SYNC, self.handle_cross_lobe_sync)
        logger.info(f"EVENT_SUBSCRIPTIONS_READY | Lobe: {self.lobe_name}")

    async def _warm_up_sdk(self):
        try:
            _ = study_sdk.registry.count_agents()
        except Exception as e:
            logger.error(f"SDK_WARMUP_FAILED | {str(e)}", trace_id="SYSTEM_BOOT")

    async def handle_user_initialization(self, payload: Dict[str, Any], trace_id: str):
        user_id = payload.get("user_id")
        if not user_id:
            return

        logger.info(f"INITIALIZING_STUDY_PROFILE | User: {user_id}", trace_id=trace_id)
        
        await mediator.publish(
            event_type=EventType.LOG_EMITTED,
            payload={"message": f"StudyFlow profile ready for {user_id}", "level": "INFO"},
            trace_id=trace_id
        )

    async def handle_cross_lobe_sync(self, payload: Dict[str, Any], trace_id: str):
        if payload.get("source_lobe") == "InsightMate" and "meeting_topics" in payload:
            logger.info("SYNCING_TOPICS_FROM_INSIGHTMATE", trace_id=trace_id)
            # Integration logic for creating study modules from meeting action items

    async def get_status(self) -> Dict[str, Any]:
        health = await study_task_registry.get_active_count()
        return {
            "lobe": self.lobe_name,
            "running": self.is_running,
            "metrics": {
                "active_sessions": health,
                "uptime": "stable"
            }
        }

app = StudyFlowApplication()

async def start_app():
    await app.start()