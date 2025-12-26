import uuid
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

from common.config.logging import logger
from common.schemas.errors import AppError, ErrorCategory
from lobes.chatbuddy.agent_sdk.state import chat_state_manager

class EmotionProfile(BaseModel):
    primary_emotion: str
    intensity: float = Field(ge=0.0, le=1.0)
    sentiment_score: float = Field(ge=-1.0, le=1.0)
    detected_traits: List[str] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0)
    analyzed_at: datetime = Field(default_factory=datetime.utcnow)

class ChatEmotionService:
    def __init__(self):
        self.default_emotion = "NEUTRAL"
        self.threshold = 0.6

    async def analyze_user_affect(
        self,
        session_id: str,
        text: str,
        trace_id: str,
        agent: Any
    ) -> EmotionProfile:
        logger.info(f"EMOTION_ANALYSIS_START | Session: {session_id} | Trace: {trace_id}")

        try:
            analysis_payload = await agent.reason(
                instruction="""
                Analyze the emotional state, sentiment, and personality traits of the user based on their input.
                Return JSON: {
                    "primary_emotion": string,
                    "intensity": float,
                    "sentiment_score": float,
                    "detected_traits": list[string],
                    "confidence": float
                }
                """,
                context={"text": text},
                trace_id=trace_id
            )

            profile = EmotionProfile(
                primary_emotion=analysis_payload.get("primary_emotion", self.default_emotion).upper(),
                intensity=analysis_payload.get("intensity", 0.5),
                sentiment_score=analysis_payload.get("sentiment_score", 0.0),
                detected_traits=analysis_payload.get("detected_traits", []),
                confidence=analysis_payload.get("confidence", 0.0)
            )

            await self._update_session_mood(session_id, profile, trace_id)
            
            return profile

        except Exception as e:
            logger.error(f"EMOTION_ANALYSIS_FAILURE | Session: {session_id} | Error: {str(e)}")
            return EmotionProfile(
                primary_emotion=self.default_emotion,
                intensity=0.0,
                sentiment_score=0.0,
                confidence=0.0
            )

    async def _update_session_mood(
        self,
        session_id: str,
        profile: EmotionProfile,
        trace_id: str
    ):
        state = chat_state_manager.get_state(session_id)
        
        current_mood_history = state.values.get("mood_trend", [])
        current_mood_history.append({
            "emotion": profile.primary_emotion,
            "sentiment": profile.sentiment_score,
            "timestamp": profile.analyzed_at.isoformat()
        })
        
        trimmed_history = current_mood_history[-10:]
        
        chat_state_manager.update_value(
            session_id=session_id,
            key="mood_trend",
            value=trimmed_history,
            trace_id=trace_id
        )
        
        chat_state_manager.update_value(
            session_id=session_id,
            key="last_emotion",
            value=profile.model_dump(),
            trace_id=trace_id
        )

    async def get_empathetic_context(self, session_id: str) -> Dict[str, Any]:
        state = chat_state_manager.get_state(session_id)
        last_emotion = state.values.get("last_emotion")
        
        if not last_emotion:
            return {"tone_suggestion": "neutral_helpful"}
            
        intensity = last_emotion.get("intensity", 0)
        emotion = last_emotion.get("primary_emotion", "NEUTRAL")
        
        if intensity > self.threshold:
            return {
                "tone_suggestion": f"acknowledge_{emotion.lower()}",
                "priority": "high",
                "traits": last_emotion.get("detected_traits", [])
            }
            
        return {"tone_suggestion": "standard_empathy"}

emotion_service = ChatEmotionService()