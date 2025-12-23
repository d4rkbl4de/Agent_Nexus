import json
import re
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Union

def format_iso_datetime(dt: Optional[datetime] = None) -> str:
    if dt is None:
        dt = datetime.now(timezone.utc)
    return dt.isoformat()

def clean_markdown_json(raw_str: str) -> str:
    json_match = re.search(r"```json\s?([\s\S]*?)```", raw_str)
    if json_match:
        return json_match.group(1).strip()
    return raw_str.strip()

def safe_json_loads(data: Union[str, bytes], default: Any = None) -> Any:
    if not data:
        return default
    try:
        return json.loads(data)
    except (json.JSONDecodeError, TypeError):
        return default

def truncate_text(text: str, max_length: int = 1000) -> str:
    if len(text) <= max_length:
        return text
    return text[:max_length].rsplit(' ', 1)[0] + "..."

def sanitize_slug(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    return re.sub(r'[-\s]+', '-', text)