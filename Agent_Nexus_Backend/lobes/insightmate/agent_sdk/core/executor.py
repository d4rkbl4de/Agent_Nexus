import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime

from common.ai_sdk.client import AgenticAISDK
from common.schemas.errors import AppError, ErrorCategory, ErrorCode
from common.config.logging_config import logger
from common.messaging.mediator import mediator
from common.messaging.schemas import EventType

from lobes.insightmate.agent_sdk.state import InsightStateManager, AnalysisState
from lobes.insightmate.agent_sdk.core.verifier import PolicyVerifier

class InsightExecutor:
    def __init__(
        self, 
        trace_id: str, 
        state: Optional[InsightStateManager] = None,
        verifier: Optional[PolicyVerifier] = None
    ):
        self.trace_id = trace_id
        self.state = state or InsightStateManager(trace_id=trace_id)
        self.verifier = verifier
        self.ai_client = AgenticAISDK()

    async def run_specific_task(self, task_id: str, inputs: Dict[str, Any]) -> Dict[str, Any]:
        transcript = inputs.get("transcript", "")
        
        if self.verifier:
            self.verifier.constraints.validate_and_block(transcript, len(transcript.encode('utf-8')) / 1024)

        try:
            if task_id == "extract_action_items":
                return await self._execute_action_item_extraction(transcript)
            elif task_id == "generate_meeting_summary":
                return await self._execute_summary_generation(transcript)
            elif task_id == "detect_sentiment_trends":
                return await self._execute_sentiment_analysis(transcript)
            else:
                raise AppError(
                    message=f"Unknown task type: {task_id}",
                    category=ErrorCategory.VALIDATION_ERROR,
                    code=ErrorCode.BAD_REQUEST,
                    trace_id=self.trace_id
                )
        except Exception as e:
            logger.error(f"EXECUTOR_TASK_FAILURE | Task: {task_id} | Error: {str(e)}", trace_id=self.trace_id)
            raise

    async def _execute_action_item_extraction(self, transcript: str) -> Dict[str, Any]:
        prompt = (
            "Extract a list of actionable tasks from the following meeting transcript. "
            "For each task, identify the owner (if mentioned) and the deadline (if mentioned). "
            "Return the result as a structured JSON list of objects with keys: 'task', 'owner', 'deadline', 'priority'."
        )
        
        response = await self.ai_client.structured_chat(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a professional project manager."},
                {"role": "user", "content": f"{prompt}\n\nTranscript:\n{transcript}"}
            ],
            trace_id=self.trace_id
        )
        
        await self.state.store_interim_result("action_items", response)
        return {"action_items": response}

    async def _execute_summary_generation(self, transcript: str) -> Dict[str, Any]:
        prompt = (
            "Provide a concise executive summary of the following meeting. "
            "Highlight the main purpose of the meeting, key decisions made, and overall outcomes. "
            "Use Markdown formatting."
        )
        
        response = await self.ai_client.chat(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a strategic executive assistant."},
                {"role": "user", "content": f"{prompt}\n\nTranscript:\n{transcript}"}
            ],
            trace_id=self.trace_id
        )
        
        await self.state.store_interim_result("executive_summary", response)
        return {"summary": response}

    async def _execute_sentiment_analysis(self, transcript: str) -> Dict[str, Any]:
        prompt = (
            "Analyze the sentiment of the meeting transcript. "
            "Identify the emotional tone of different segments and note any significant shifts in group dynamics. "
            "Identify if the meeting ended on a positive, neutral, or negative note."
        )
        
        response = await self.ai_client.structured_chat(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an organizational psychologist."},
                {"role": "user", "content": f"{prompt}\n\nTranscript:\n{transcript}"}
            ],
            trace_id=self.trace_id
        )
        
        await self.state.store_interim_result("sentiment_analysis", response)
        return {"sentiment_trends": response}

    async def finalize_analysis(self) -> Dict[str, Any]:
        state = await self.state.get_state()
        results = state.interim_results
        
        final_payload = {
            "session_id": state.session_id,
            "agent_id": state.agent_id,
            "completed_at": datetime.utcnow().isoformat(),
            "results": results
        }
        
        await mediator.publish(
            event_type=EventType.DATA_SYNC,
            payload=final_payload,
            trace_id=self.trace_id
        )
        
        return final_payload