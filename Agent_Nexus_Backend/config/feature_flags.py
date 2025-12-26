from pydantic_settings import BaseSettings
from typing import Dict, Any, Optional
from enum import Enum
import os

class FeatureState(str, Enum):
    ENABLED = "enabled"
    DISABLED = "disabled"
    BETA = "beta"
    EXPERIMENTAL = "experimental"

class FeatureFlags(BaseSettings):
    AGENT_ORCHESTRATION_V2: FeatureState = FeatureState.EXPERIMENTAL
    VECTOR_SEARCH_RECONFIG: FeatureState = FeatureState.BETA
    STREAMING_THOUGHTS: FeatureState = FeatureState.ENABLED
    AUTONOMOUS_TOOL_USE: FeatureState = FeatureState.DISABLED
    MEMORY_COMPRESSION: FeatureState = FeatureState.EXPERIMENTAL
    
    ENVIRONMENT: str = os.getenv("ENV", "development")
    
    _OVERRIDE_MAP: Dict[str, FeatureState] = {}

    def is_active(self, feature_name: str, user_context: Optional[Dict[str, Any]] = None) -> bool:
        feature = getattr(self, feature_name.upper(), FeatureState.DISABLED)
        
        if feature == FeatureState.ENABLED:
            return True
        if feature == FeatureState.DISABLED:
            return False
            
        if feature == FeatureState.BETA:
            if user_context and user_context.get("is_internal", False):
                return True
            return False
            
        if feature == FeatureState.EXPERIMENTAL:
            return self.ENVIRONMENT == "development"
            
        return False

    def get_all_flags(self) -> Dict[str, str]:
        return {
            name: val.value for name, val in self.dict().items() 
            if isinstance(val, FeatureState)
        }

    class Config:
        case_sensitive = True
        env_prefix = "FEATURE_"

feature_flags = FeatureFlags()