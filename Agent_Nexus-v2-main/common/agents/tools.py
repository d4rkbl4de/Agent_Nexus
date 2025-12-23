import httpx
from common.config.logging_config import logger
from common.config.settings import settings

class ExternalToolClient:
    """
    A client to interact with external, third-party APIs (not the internal Lobes).
    This handles common HTTP configurations, retries, and logging for external calls.
    """
    def __init__(self):
        # We can configure a base client with common headers and timeouts here
        self.client = httpx.AsyncClient(timeout=30.0)

    async def call_crm_api(self, endpoint: str, data: dict):
        """Mock method to call an external CRM service."""
        crm_url = "https://api.external-crm.com"  # Example external URL
        full_url = f"{crm_url}/{endpoint}"
        
        logger.info(f"ExternalToolClient: Calling CRM endpoint: {endpoint}", extra={"url": full_url})
        
        headers = {
            "Authorization": f"Bearer {settings().SECRET_KEY}",  # Use a relevant external key
            "Content-Type": "application/json"
        }
        
        try:
            response = await self.client.post(full_url, json=data, headers=headers)
            response.raise_for_status()
            logger.info(f"CRM API call to {endpoint} successful.")
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"External CRM API HTTP error at {endpoint}: {e.response.status_code}")
            return {"error": f"HTTP error {e.response.status_code}"}
        except httpx.RequestError as e:
            logger.error(f"External CRM API request error at {endpoint}: {e}")
            return {"error": "Request failed"}

# Create a single instance to be imported throughout the application
EXTERNAL_TOOL_CLIENT = ExternalToolClient()