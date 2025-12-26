import json
from typing import Dict, Optional
from tracing.context import get_trace_id, get_agent_id, get_task_id, set_trace_context
from common.config.logging import logger

def inject_trace_headers(headers: Optional[Dict[str, str]] = None) -> Dict[str, str]:
    if headers is None:
        headers = {}
    
    headers["X-Trace-ID"] = get_trace_id()
    
    agent_id = get_agent_id()
    if agent_id:
        headers["X-Agent-ID"] = agent_id
        
    task_id = get_task_id()
    if task_id:
        headers["X-Task-ID"] = task_id
        
    return headers

def extract_trace_headers(headers: Dict[str, str]) -> None:
    trace_id = headers.get("X-Trace-ID") or headers.get("x-trace-id")
    agent_id = headers.get("X-Agent-ID") or headers.get("x-agent-id")
    task_id = headers.get("X-Task-ID") or headers.get("x-task-id")
    
    if trace_id:
        set_trace_context(trace_id=trace_id, agent_id=agent_id, task_id=task_id)
    else:
        logger.debug("No trace headers found in extraction target; starting new context")
        set_trace_context()

def pack_trace_for_queue() -> str:
    return json.dumps({
        "trace_id": get_trace_id(),
        "agent_id": get_agent_id(),
        "task_id": get_task_id()
    })

def unpack_trace_from_queue(packed_data: str) -> None:
    try:
        data = json.loads(packed_data)
        set_trace_context(
            trace_id=data.get("trace_id"),
            agent_id=data.get("agent_id"),
            task_id=data.get("task_id")
        )
    except (json.JSONDecodeError, AttributeError) as e:
        logger.error(f"Failed to unpack trace context from queue: {str(e)}")
        set_trace_context()