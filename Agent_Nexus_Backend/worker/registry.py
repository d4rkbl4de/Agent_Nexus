import importlib
from typing import Dict, Callable, Any
from celery import shared_task
from common.config.logging import logger
from tracing.context import set_trace_id, set_agent_id

class TaskRegistry:
    def __init__(self):
        self._tasks: Dict[str, str] = {
            "insightmate.summarize": "InsightMate.tasks.summarize_meeting",
            "insightmate.extract_actions": "InsightMate.tasks.extract_action_items",
            "studyflow.generate_quiz": "StudyFlow.tasks.create_study_material",
            "studyflow.analyze_paper": "StudyFlow.tasks.process_research_pdf",
            "chatbuddy.process_message": "ChatBuddyPlus.tasks.handle_chat_logic",
            "autoagent.orchestrate": "AutoAgent_Hub.tasks.run_master_loop",
        }

    def get_task_path(self, task_name: str) -> str:
        path = self._tasks.get(task_name)
        if not path:
            logger.error(f"Task registration missing: {task_name}")
            raise ValueError(f"Task '{task_name}' is not registered in the Hive Mind.")
        return path

task_registry = TaskRegistry()

@shared_task(bind=True, name="hive_mind.dispatch_task")
def dispatch_task(self, task_name: str, payload: Dict[str, Any], trace_id: str = None):
    set_trace_id(trace_id or self.request.id)
    
    try:
        task_path = task_registry.get_task_path(task_name)
        module_path, func_name = task_path.rsplit(".", 1)
        
        module = importlib.import_module(module_path)
        task_func = getattr(module, func_name)
        
        set_agent_id(module_path.split(".")[0])
        
        logger.info(f"Executing task: {task_name} | Trace: {trace_id}")
        return task_func(**payload)
        
    except Exception as e:
        logger.error(f"Execution Error in {task_name}: {str(e)} | Trace: {trace_id}")
        raise self.retry(exc=e, countdown=5, max_retries=3)