import os
from celery import Celery
from common.config.settings import settings
from common.config.logging import logger
from worker.bootstrap import bootstrap_worker

celery_app = Celery(
    "agent_nexus_worker",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["worker.registry"]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=100,
    broker_connection_retry_on_startup=True
)

@celery_app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    logger.info("Configuring periodic health checks for Hive Mind workers.")

@celery_app.task(name="worker.heartbeat")
def heartbeat():
    return {"status": "online", "worker_id": os.uname().nodename}

class AgentWorker(celery_app.Task):
    _context = None

    def __call__(self, *args, **kwargs):
        if self._context is None:
            self._context = bootstrap_worker()
        return self.run(*args, **kwargs)

if __name__ == "__main__":
    celery_app.start()