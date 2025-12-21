import os
import requests
import json
import time
from typing import Dict, Any, List

# --- Core Configuration ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
QDRANT_HOST = os.getenv("QDRANT_HOST")
REDIS_URL = os.getenv("REDIS_URL")
DATABASE_URL = os.getenv("DATABASE_URL")

# LLM API Setup
LLM_MODEL = "gemini-2.5-flash-preview-09-2025"
LLM_API_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models"
LLM_API_URL = f"{LLM_API_BASE_URL}/{LLM_MODEL}:generateContent?key={GEMINI_API_KEY}"


def call_gemini_api(
    prompt: str,
    system_instruction: str = "",
    use_grounding: bool = False,
    retries: int = 3
) -> Dict[str, Any]:
    """
    Calls the Gemini API with exponential backoff and handles grounding (Google Search).
    """
    if not GEMINI_API_KEY:
        return {"text": "API Key is missing. Cannot perform LLM call.", "sources": []}

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
    }
    
    if system_instruction:
        payload["config"] = {"systemInstruction": system_instruction} # Updated to use 'config' for system instruction

    if use_grounding:
        # Grounding is enabled via the tools parameter in the config
        payload.setdefault("config", {})["tools"] = [{"googleSearch": {}}] 

    headers = {'Content-Type': 'application/json'}
    
    for attempt in range(retries):
        try:
            response = requests.post(LLM_API_URL, headers=headers, data=json.dumps(payload), timeout=15)
            response.raise_for_status()
            
            result = response.json()
            candidate = result.get('candidates', [{}])[0]
            
            text = candidate.get('content', {}).get('parts', [{}])[0].get('text', 'No text generated.')
            
            sources: List[Dict[str, str]] = []
            grounding_metadata = candidate.get('groundingMetadata', {})
            if grounding_metadata and grounding_metadata.get('groundingAttributions'):
                sources = [
                    {"uri": attr.get('web', {}).get('uri'), "title": attr.get('web', {}).get('title')}
                    for attr in grounding_metadata['groundingAttributions']
                    if attr.get('web', {}).get('uri') and attr.get('web', {}).get('title')
                ]
            
            return {"text": text, "sources": sources}

        except requests.exceptions.RequestException as e:
            if attempt < retries - 1:
                sleep_time = 2 ** attempt
                print(f"API call failed: {e}. Retrying in {sleep_time} seconds...")
                time.sleep(sleep_time)
            else:
                return {"text": f"LLM API failed after {retries} attempts: {e}", "sources": []}
    
    return {"text": "Unknown error during LLM API call.", "sources": []}

# Placeholder for Qdrant and Database Clients (not implemented for brevity)
def get_qdrant_client():
    return f"Qdrant Client at {QDRANT_HOST}"

def get_db_connection():
    return f"DB Connection to {DATABASE_URL}"