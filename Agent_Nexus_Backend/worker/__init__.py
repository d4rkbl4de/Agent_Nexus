# Generic worker package initialization
from typing import Dict, Any, Type
from worker.registry import task_registry
from worker.bootstrap import bootstrap_worker
from worker.app import worker_app

class WorkerManifest:
    def __init__(self):
        self.app = worker_app
        self.registry = task_registry
        self.bootstrap = bootstrap_worker

    async def initialize(self):
        await self.bootstrap.setup()

    def get_registered_tasks(self) -> Dict[str, Any]:
        return self.registry.list_tasks()

worker_manifest = WorkerManifest()

__all__ = [
    "worker_app",
    "task_registry",
    "bootstrap_worker",
    "worker_manifest"
]