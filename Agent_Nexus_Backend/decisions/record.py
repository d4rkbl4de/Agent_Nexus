import json
import aiofiles
from typing import Any, Dict
from datetime import datetime
from pathlib import Path
from common.config.logging import logger
from decisions.proposal import ActionProposal
from decisions.verdict import DecisionVerdict
from common.schemas.errors import AppError, ErrorCategory

class DecisionRecorder:
    def __init__(self, log_dir: str = "logs/decisions"):
        self.log_path = Path(log_dir)
        self._ensure_log_dir()

    def _ensure_log_dir(self) -> None:
        self.log_path.mkdir(parents=True, exist_ok=True)

    async def record_event(self, proposal: ActionProposal, verdict: DecisionVerdict) -> None:
        trace_id = proposal.trace_id
        
        record = {
            "timestamp": datetime.utcnow().isoformat(),
            "trace_id": trace_id,
            "agent_id": proposal.agent_id,
            "lobe": proposal.lobe,
            "proposal": proposal.model_dump(),
            "verdict": verdict.model_dump(),
            "performance": {
                "estimated_cost": proposal.estimated_cost,
                "priority": proposal.priority
            }
        }

        try:
            filename = f"{datetime.utcnow().strftime('%Y-%m-%d')}_decisions.jsonl"
            target_file = self.log_path / filename
            
            async with aiofiles.open(target_file, mode='a', encoding='utf-8') as f:
                await f.write(json.dumps(record) + "\n")
            
            logger.info(f"DECISION_ARCHIVED | Trace: {trace_id} | Status: {verdict.status.value}")
        
        except Exception as e:
            logger.error(f"AUDIT_LOG_CRITICAL_FAILURE | Trace: {trace_id} | Error: {str(e)}")
            raise AppError(
                message="Critical failure writing to decision audit log",
                category=ErrorCategory.INTERNAL_ERROR,
                status_code=500
            )

    async def get_trace_history(self, trace_id: str) -> list[Dict[str, Any]]:
        history = []
        try:
            for log_file in sorted(self.log_path.glob("*.jsonl"), reverse=True):
                async with aiofiles.open(log_file, mode='r', encoding='utf-8') as f:
                    async for line in f:
                        entry = json.loads(line)
                        if entry.get("trace_id") == trace_id:
                            history.append(entry)
            return history
        except Exception as e:
            logger.error(f"TRACE_RETRIEVAL_FAILED | Trace: {trace_id} | Error: {str(e)}")
            return []

decision_recorder = DecisionRecorder()