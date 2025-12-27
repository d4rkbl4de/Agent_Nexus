import time
from uuid import uuid4
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, BackgroundTasks, Body, Query

from common.schemas.api_response import APIResponse, wrap_success
from common.schemas.errors import AppError, ErrorCategory, ErrorCode
from common.config.logging_config import logger
from common.messaging.mediator import mediator
from common.messaging.schemas import EventType

from lobes.studyflow.agent_sdk import study_sdk
from lobes.studyflow.api.v1.schemas import (
    StudySessionRequest,
    StudySessionResponse,
    TutorInteractionRequest,
    TutorInteractionResponse,
    CurriculumResponse
)

router = APIRouter()

@router.post("/sessions", response_model=APIResponse[StudySessionResponse])
async def create_study_session(
    background_tasks: BackgroundTasks,
    request: StudySessionRequest = Body(...)
):
    trace_id = request.trace_id or str(uuid4())
    session_id = f"st_sess_{uuid4().hex[:8]}"
    
    try:
        engine = await study_sdk.create_learning_engine(
            agent_id=request.agent_id,
            trace_id=trace_id,
            user_id=request.user_id,
            session_id=session_id
        )

        await engine["state"].initialize_session(
            session_id=session_id,
            agent_id=request.agent_id,
            subject=request.subject,
            difficulty=request.difficulty
        )

        background_tasks.add_task(
            _async_curriculum_generation,
            engine=engine,
            subject=request.subject,
            goals=request.goals,
            trace_id=trace_id
        )

        data = StudySessionResponse(
            session_id=session_id,
            status="initializing",
            trace_id=trace_id
        )
        return wrap_success(data, trace_id=trace_id, lobe="StudyFlow")

    except AppError as e:
        raise HTTPException(status_code=e.status_code, detail=e.to_dict())

@router.post("/sessions/{session_id}/interact", response_model=APIResponse[TutorInteractionResponse])
async def interact_with_tutor(
    session_id: str,
    request: TutorInteractionRequest = Body(...)
):
    trace_id = request.trace_id or str(uuid4())
    try:
        engine = await study_sdk.create_learning_engine(
            agent_id=request.agent_id,
            trace_id=trace_id,
            user_id=request.user_id,
            session_id=session_id
        )
        
        result = await engine["tutor"].generate_response(request.message)
        
        data = TutorInteractionResponse(
            session_id=session_id,
            response=result["tutor_message"],
            evaluation=result["evaluation"],
            next_step=result["suggested_next_topic"]
        )
        return wrap_success(data, trace_id=trace_id, lobe="StudyFlow")
    except Exception as e:
        logger.error(f"TUTOR_INTERACTION_FAILED | Session: {session_id} | Error: {str(e)}")
        raise HTTPException(status_code=500, detail="Interaction failed")

@router.get("/sessions/{session_id}/curriculum", response_model=APIResponse[CurriculumResponse])
async def get_curriculum(session_id: str, user_id: str = Query(...), trace_id: str = Query(...)):
    try:
        state_manager = study_sdk.StudyStateManager(trace_id=trace_id, user_id=user_id)
        state = await state_manager.get_state()
        
        data = CurriculumResponse(
            session_id=session_id,
            subject=state.subject,
            pathway=state.curriculum_path,
            completed=state.completed_topics,
            gaps=list(state.knowledge_gaps.keys())
        )
        return wrap_success(data, trace_id=trace_id, lobe="StudyFlow")
    except Exception:
        raise HTTPException(status_code=404, detail="Session curriculum not found")

async def _async_curriculum_generation(engine: Dict[str, Any], subject: str, goals: str, trace_id: str):
    try:
        planner = engine["planner"]
        state = engine["state"]
        
        curriculum = await planner.generate_curriculum(subject=subject, user_goals=goals)
        
        module_titles = [m.title for m in curriculum.modules]
        await state.set_curriculum(module_titles)
        
        await mediator.publish(
            event_type=EventType.TASK_COMPLETED,
            payload={
                "session_id": engine["session_id"],
                "type": "curriculum_ready",
                "modules_count": len(module_titles)
            },
            trace_id=trace_id
        )
    except Exception as e:
        logger.error(f"ASYNC_CURRICULUM_FAILED | Trace: {trace_id} | Error: {str(e)}")