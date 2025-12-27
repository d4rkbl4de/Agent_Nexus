from typing import Dict, Any, Optional
from enum import Enum
from pydantic import BaseModel, Field
from common.ai_sdk.client import AgenticAISDK
from common.config.logging_config import logger
from common.schemas.errors import AppError, ErrorCategory, ErrorCode

class EmotionalState(str, Enum):
    NEUTRAL = "neutral"
    JOY = "joy"
    FRUSTRATION = "frustration"
    ANXIETY = "anxiety"
    SADNESS = "sadness"
    EXCITEMENT = "excitement"
    CONFUSION = "confusion"

class EmotionalAnalysis(BaseModel):
    primary_emotion: EmotionalState
    confidence_score: float = Field(ge=0, le=1)
    intensity: float = Field(ge=0, le=1)
    sentiment_score: float = Field(ge=-1, le=1)
    suggested_tone_shift: Optional[str] = None

class EmotionalIntelligenceEngine:
    def __init__(self, trace_id: str):
        self.trace_id = trace_id
        self.ai_client = AgenticAISDK()
        self.analysis_model = "gpt-4o-mini"

    async def analyze_input(self, text: str, history: Optional[str] = None) -> EmotionalAnalysis:
        try:
            prompt = self._build_analysis_prompt(text, history)
            response = await self.ai_client.structured_output(
                model=self.analysis_model,
                prompt=prompt,
                response_format=EmotionalAnalysis,
                trace_id=self.trace_id
            )
            
            logger.info(
                f"EMOTIONAL_ANALYSIS_COMPLETE | Emotion: {response.primary_emotion}",
                trace_id=self.trace_id,
                extra={"sentiment": response.sentiment_score}
            )
            return response

        except Exception as e:
            logger.error(
                f"EMOTIONAL_ANALYSIS_FAILED | Trace: {self.trace_id}",
                trace_id=self.trace_id,
                extra={"error": str(e)}
            )
            return EmotionalAnalysis(
                primary_emotion=EmotionalState.NEUTRAL,
                confidence_score=1.0,
                intensity=0.0,
                sentiment_score=0.0
            )

    def get_empathetic_refinement(self, analysis: EmotionalAnalysis, base_response: str) -> str:
        if analysis.intensity < 0.4 and analysis.primary_emotion == EmotionalState.NEUTRAL:
            return base_response

        adjustments = {
            EmotionalState.FRUSTRATION: "Acknowledge the difficulty and offer clear, immediate assistance.",
            EmotionalState.ANXIETY: "Use calming, reassuring language and simplify the next steps.",
            EmotionalState.JOY: "Mirror the enthusiasm and celebrate the user's success.",
            EmotionalState.SADNESS: "Use a softer, supportive tone with high empathy markers."
        }
        
        instruction = adjustments.get(analysis.primary_emotion, "Maintain a helpful and balanced tone.")
        return f"[Tone Instruction: {instruction}] {base_response}"

    def _build_analysis_prompt(self, text: str, history: Optional[str]) -> str:
        context = f"\nConversation History Context: {history}" if history else ""
        return (
            "Analyze the emotional state of the following user input. "
            "Consider word choice, punctuation, and underlying sentiment. "
            f"Input: '{text}'{context}"
        )