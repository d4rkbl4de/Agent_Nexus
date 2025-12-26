import contextvars
import uuid
from typing import Optional

trace_var: contextvars.ContextVar[str] = contextvars.ContextVar("trace_id", default="")
agent_var: contextvars.ContextVar[str] = contextvars.ContextVar("agent_id", default="")
task_var: contextvars.ContextVar[str] = contextvars.ContextVar("task_id", default="")

def set_trace_context(trace_id: Optional[str] = None, agent_id: Optional[str] = None, task_id: Optional[str] = None) -> None:
    trace_var.set(trace_id or str(uuid.uuid4()))
    if agent_id:
        agent_var.set(agent_id)
    if task_id:
        task_var.set(task_id)

def get_trace_id() -> str:
    tid = trace_var.get()
    if not tid:
        new_id = str(uuid.uuid4())
        trace_var.set(new_id)
        return new_id
    return tid

def get_agent_id() -> Optional[str]:
    return agent_var.get() or None

def get_task_id() -> Optional[str]:
    return task_var.get() or None

def clear_trace_context() -> None:
    trace_var.set("")
    agent_var.set("")
    task_var.set("")