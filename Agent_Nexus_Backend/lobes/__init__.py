from typing import Dict, Any, List
from common.config.logging_config import logger
from common.schemas.errors import AppError, ErrorCategory, ErrorCode

class LobeRegistry:
    def __init__(self):
        self._lobes: Dict[str, Any] = {}
        self._initialized = False

    def register_lobe(self, name: str, instance: Any):
        if name in self._lobes:
            raise AppError(
                message=f"Lobe collision: {name} already registered",
                category=ErrorCategory.INTERNAL_ERROR,
                code=ErrorCode.SYSTEM_PANIC
            )
        self._lobes[name] = instance
        logger.info(f"LOBE_LOADED | Name: {name}", trace_id="SYSTEM_BOOT")

    async def initialize_all(self):
        if self._initialized:
            return
        
        for name, instance in self._lobes.items():
            if hasattr(instance, "start"):
                await instance.start()
        
        self._initialized = True
        logger.info("ALL_LOBES_INITIALIZED", trace_id="SYSTEM_BOOT")

    def get_lobe(self, name: str) -> Any:
        lobe = self._lobes.get(name)
        if not lobe:
            raise AppError(
                message=f"Lobe {name} not found in registry",
                category=ErrorCategory.NOT_FOUND_ERROR,
                code=ErrorCode.RESOURCE_NOT_FOUND
            )
        return lobe

    def list_active_lobes(self) -> List[str]:
        return list(self._lobes.keys())

lobe_registry = LobeRegistry()

try:
    from lobes.chatbuddy import lobe as chatbuddy_lobe
    lobe_registry.register_lobe("ChatBuddy", chatbuddy_lobe)
except ImportError:
    logger.warning("LOBE_IMPORT_FAILED | ChatBuddy not found")

try:
    from lobes.insightmate import lobe as insightmate_lobe
    lobe_registry.register_lobe("InsightMate", insightmate_lobe)
except ImportError:
    logger.warning("LOBE_IMPORT_FAILED | InsightMate not found")

__all__ = ["lobe_registry"]