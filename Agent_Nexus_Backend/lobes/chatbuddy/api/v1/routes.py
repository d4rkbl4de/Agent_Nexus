from fastapi import APIRouter, Depends, HTTPException, Body
from fastapi.responses import StreamingResponse
from typing import List, Optional
from uuid import uuid4

from common.schemas.api_response import APIResponse, wrap_success
from common.schemas.errors import AppError, ErrorCategory, ErrorCode
from lobes.chatbuddy.agent_sdk import chat_sdk
from lobes.chatbuddy.api.v1.schemas import ChatRequest, ChatSessionResponse, AgentMetadata
from common.config.logging_config import logger

router = APIRouter()

@router.post("/sessions", response_model=APIResponse[ChatSessionResponse])
async def create_chat_session(
    agent_id: str = Body(..., embed=True),
    user_id: str = Body(..., embed=True)
):
    trace_id = str(uuid4())
    try:
        engine = await chat_sdk.create_engine(
            agent_id=agent_id,
            trace_id=trace_id,
            user_id=user_id
        )
        
        data = ChatSessionResponse(
            session_id=engine.session_id,
            trace_id=trace_id,
            agent_metadata=AgentMetadata(**engine.definition.model_dump())
        )
        
        return wrap_success(data, trace_id=trace_id, lobe="ChatBuddy")
    except AppError as e:
        raise HTTPException(status_code=e.status_code, detail=e.to_dict())

@router.post("/chat/stream")
async def stream_chat(request: ChatRequest):
    trace_id = request.trace_id or str(uuid4())
    
    async def event_generator():
        try:
            engine = await chat_sdk.create_engine(
                agent_id=request.agent_id,
                trace_id=trace_id,
                user_id=request.user_id,
                session_id=request.session_id
            )
            
            async for chunk in engine.chat_stream(request.message):
                yield f"data: {chunk}\n\n"
                
            yield "data: [DONE]\n\n"
            
        except Exception as e:
            logger.error(f"STREAM_ERROR | Trace: {trace_id} | Error: {str(e)}")
            yield f"data: {{\"error\": \"{str(e)}\"}}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

@router.get("/agents", response_model=APIResponse[List[AgentMetadata]])
async def list_available_buddies():
    trace_id = str(uuid4())
    agents = chat_sdk.registry.list_agents()
    data = [AgentMetadata(**a.model_dump()) for a in agents]
    return wrap_success(data, trace_id=trace_id, lobe="ChatBuddy")

@router.delete("/sessions/{session_id}")
async def terminate_session(session_id: str, user_id: str):
    trace_id = str(uuid4())

    return wrap_success({"status": "terminated"}, trace_id=trace_id, lobe="ChatBuddy")