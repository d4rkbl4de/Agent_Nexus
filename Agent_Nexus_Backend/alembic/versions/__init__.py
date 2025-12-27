import os
import importlib
from typing import List

def get_migration_versions() -> List[str]:
    versions_dir = os.path.dirname(__file__)
    versions = []
    for filename in os.listdir(versions_dir):
        if filename.endswith(".py") and not filename.startswith("__"):
            versions.append(filename[:-3])
    return sorted(versions)

def load_version_module(version_id: str):
    try:
        module_path = f"alembic.versions.{version_id}"
        return importlib.import_module(module_path)
    except ImportError:
        return None

__all__ = [
    "get_migration_versions",
    "load_version_module"
]