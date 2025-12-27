import time
from uuid import uuid4
from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException, BackgroundTasks, Body

from common.schemas.api_response import APIResponse, wrap_success
from common.schemas.errors import AppError, ErrorCategory, ErrorCode
from common.config.logging_config import logger
from common.messaging.mediator import mediator
from common.messaging.schemas import EventType

from lobes.insightmate.agent_sdk import insight_sdk
from lobes.insightmate.api.v1.schemas import (
    AnalysisRequest, 
    AnalysisSessionResponse, 
    AnalysisDetailResponse,
    AnalysisResult
)

router = APIRouter()

@router.post("/analyze", response_model=APIResponse[AnalysisSessionResponse])
async def trigger_meeting_analysis(
    background_tasks: BackgroundTasks,
    request: AnalysisRequest = Body(...)
):
    trace_id = request.trace_id or str(uuid4())
    session_id = f"ins_{int(time.time())}_{uuid4().hex[:6]}"
    
    try:
        engine_context = await insight_sdk.create_analysis_engine(
            agent_id=request.agent_id,
            trace_id=trace_id,
            user_id="SYSTEM_OWNER",
            session_id=session_id
        )

        background_tasks.add_task(
            process_analysis_pipeline,
            engine_context=engine_context,
            request=request,
            trace_id=trace_id
        )

        data = AnalysisSessionResponse(
            session_id=session_id,
            trace_id=trace_id,
            status="accepted",
            estimated_completion_ms=15000
        )
        
        return wrap_success(data, trace_id=trace_id, lobe="InsightMate")

    except AppError as e:
        raise HTTPException(status_code=e.status_code, detail=e.to_dict())

@router.get("/sessions/{session_id}", response_model=APIResponse[AnalysisDetailResponse])
async def get_analysis_status(session_id: str, trace_id: str):
    try:
        state_manager = insight_sdk.InsightStateManager(trace_id=trace_id)
        state = await state_manager.get_state()
        
        data = AnalysisDetailResponse(
            session_id=state.session_id,
            agent_id=state.agent_id,
            status=state.current_step,
            result=AnalysisResult(
                summary=state.interim_results.get("executive_summary"),
                action_items=state.interim_results.get("action_items", []),
                sentiment_trends=state.interim_results.get("sentiment_analysis"),
                metadata={"progress": f"{state.processed_chunks}/{state.total_chunks}"}
            )
        )
        return wrap_success(data, trace_id=trace_id, lobe="InsightMate")
    except Exception as e:
        logger.error(f"SESSION_FETCH_FAILED | Session: {session_id} | Error: {str(e)}")
        raise HTTPException(status_code=404, detail="Session not found or trace_id mismatch")

async def process_analysis_pipeline(engine_context: Dict[str, Any], request: AnalysisRequest, trace_id: str):
    planner = engine_context["planner"]
    executor = engine_context["executor"]
    state = engine_context["state"]
    
    try:
        await state.initialize_state(
            session_id=engine_context["session_id"],
            agent_id=request.agent_id,
            transcript_hash=str(hash(request.transcript))
        )

        plan = await planner.create_plan({"length": len(request.transcript), "tasks": request.tasks})
        chunks = await planner.decompose_transcript(request.transcript)
        await state.update_progress("executing", 0, len(chunks))

        for task_id in request.tasks:
            await executor.run_specific_task(task_id, {"transcript": request.transcript})
        
        await executor.finalize_analysis()
        await state.update_progress("completed", len(chunks))

    except Exception as e:
        logger.error(f"PIPELINE_CRITICAL_FAILURE | Trace: {trace_id} | Error: {str(e)}")
        await mediator.publish(
            event_type=EventType.TASK_FAILED,
            payload={"error": str(e), "session_id": engine_context["session_id"]},
            trace_id=trace_id
        )