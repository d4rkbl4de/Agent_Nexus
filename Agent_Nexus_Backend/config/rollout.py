from pydantic_settings import BaseSettings
from typing import Dict, List, Optional, Any
from enum import Enum
import hashlib

class RolloutStrategy(str, Enum):
    DIRECT = "direct"
    CANARY = "canary"
    PERCENTAGE = "percentage"
    USER_ID = "user_id"

class RolloutConfig(BaseSettings):
    DEFAULT_STRATEGY: RolloutStrategy = RolloutStrategy.PERCENTAGE
    GLOBAL_PERCENTAGE: float = 0.10
    CANARY_GROUPS: Dict[str, List[str]] = {
        "alpha_testers": [],
        "internal_devs": []
    }
    
    LOBE_OVERRIDES: Dict[str, Dict[str, Any]] = {
        "autoagent_hub": {"strategy": "canary", "group": "internal_devs"},
        "insightmate": {"strategy": "percentage", "value": 0.05}
    }

    def should_activate(
        self, 
        feature_key: str, 
        identifier: Optional[str] = None, 
        lobe_context: Optional[str] = None
    ) -> bool:
        config = self.LOBE_OVERRIDES.get(lobe_context, {}) if lobe_context else {}
        strategy = config.get("strategy", self.DEFAULT_STRATEGY)

        if strategy == RolloutStrategy.DIRECT:
            return True

        if strategy == RolloutStrategy.CANARY:
            group_name = config.get("group", "internal_devs")
            allowed_ids = self.CANARY_GROUPS.get(group_name, [])
            return identifier in allowed_ids if identifier else False

        if strategy == RolloutStrategy.PERCENTAGE:
            if not identifier:
                return False
            threshold = config.get("value", self.GLOBAL_PERCENTAGE)
            hash_val = hashlib.md5(f"{feature_key}:{identifier}".encode()).hexdigest()
            return (int(hash_val, 16) % 100) < (threshold * 100)

        return False

    class Config:
        case_sensitive = True
        env_prefix = "ROLLOUT_"

rollout_config = RolloutConfig()