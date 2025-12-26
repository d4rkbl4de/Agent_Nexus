import hashlib
from typing import Any, Dict, List, Optional
from common.config.logging import logger
from common.ai_sdk.exceptions import RoutingException

class AIRouter:
    def __init__(self):
        self.routes = {
            "reasoning": {"provider": "openai", "model": "gpt-4-turbo"},
            "speed": {"provider": "gemini", "model": "gemini-1.5-flash"},
            "balanced": {"provider": "openai", "model": "gpt-3.5-turbo"},
            "fallback": {"provider": "openrouter", "model": "anthropic/claude-3-haiku"}
        }
        self.capability_map = {
            "planning": "reasoning",
            "extraction": "speed",
            "summarization": "speed",
            "coding": "reasoning",
            "chat": "balanced"
        }

    def get_route(
        self, 
        prompt: str, 
        override: Optional[str] = None, 
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, str]:
        if override:
            return self._resolve_override(override)

        intent = self._identify_intent(prompt, context)
        route_key = self.capability_map.get(intent, "balanced")
        
        selected_route = self.routes.get(route_key)
        
        if not selected_route:
            logger.warning(f"ROUTING_FALLBACK_TRIGGERED | Intent: {intent}")
            return self.routes["fallback"]

        return selected_route

    def _identify_intent(self, prompt: str, context: Optional[Dict[str, Any]]) -> str:
        if context and "capability" in context:
            return context["capability"]
        
        prompt_lower = prompt.lower()
        if any(kw in prompt_lower for kw in ["plan", "analyze", "strategy", "complex"]):
            return "planning"
        if any(kw in prompt_lower for kw in ["format", "json", "extract", "clean"]):
            return "extraction"
        if any(kw in prompt_lower for kw in ["code", "python", "script", "refactor"]):
            return "coding"
            
        return "chat"

    def _resolve_override(self, override: str) -> Dict[str, str]:
        parts = override.split("/")
        if len(parts) == 2:
            return {"provider": parts[0], "model": parts[1]}
        
        for key, route in self.routes.items():
            if override == key:
                return route
            if override == route["model"]:
                return route

        raise RoutingException(f"Invalid model override: {override}")

    def get_health_status(self) -> Dict[str, bool]:
        return {provider: True for provider in ["openai", "gemini", "openrouter"]}