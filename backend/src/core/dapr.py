"""Dapr client wrapper for pub/sub and state management."""

import logging
import os
from typing import Any

import httpx

logger = logging.getLogger(__name__)

# Dapr configuration from environment
DAPR_HTTP_PORT = int(os.getenv("DAPR_HTTP_PORT", "3500"))
PUBSUB_NAME = os.getenv("DAPR_PUBSUB_NAME", "taskpubsub")
STATE_STORE_NAME = os.getenv("DAPR_STATE_STORE", "statestore")

# Feature flag to enable/disable Dapr
DAPR_ENABLED = os.getenv("DAPR_ENABLED", "false").lower() == "true"


class DaprClient:
    """Client for interacting with Dapr building blocks."""

    def __init__(self):
        """Initialize Dapr client."""
        self.base_url = f"http://localhost:{DAPR_HTTP_PORT}"
        self.pubsub_name = PUBSUB_NAME
        self.state_store = STATE_STORE_NAME
        self.enabled = DAPR_ENABLED
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create async HTTP client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(timeout=30.0)
        return self._client

    async def close(self):
        """Close the HTTP client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()

    async def publish(self, topic: str, data: dict[str, Any]) -> bool:
        """
        Publish a message to a topic.

        Args:
            topic: Topic name (e.g., "task-events")
            data: Message payload

        Returns:
            True if successful, False otherwise
        """
        if not self.enabled:
            logger.debug(f"Dapr disabled, skipping publish to {topic}")
            return True

        url = f"{self.base_url}/v1.0/publish/{self.pubsub_name}/{topic}"
        try:
            client = await self._get_client()
            response = await client.post(
                url,
                json=data,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            logger.info(f"Published event to {topic}")
            return True
        except httpx.HTTPStatusError as e:
            logger.error(f"Failed to publish to {topic}: HTTP {e.response.status_code}")
            return False
        except httpx.RequestError as e:
            logger.error(f"Failed to publish to {topic}: {e}")
            return False

    async def get_state(self, key: str) -> Any | None:
        """
        Get state by key.

        Args:
            key: State key

        Returns:
            State value or None if not found
        """
        if not self.enabled:
            logger.debug(f"Dapr disabled, skipping get_state for {key}")
            return None

        url = f"{self.base_url}/v1.0/state/{self.state_store}/{key}"
        try:
            client = await self._get_client()
            response = await client.get(url)
            if response.status_code == 204:
                return None
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"Failed to get state {key}: HTTP {e.response.status_code}")
            return None
        except httpx.RequestError as e:
            logger.error(f"Failed to get state {key}: {e}")
            return None

    async def save_state(self, key: str, value: Any) -> bool:
        """
        Save state.

        Args:
            key: State key
            value: State value

        Returns:
            True if successful, False otherwise
        """
        if not self.enabled:
            logger.debug(f"Dapr disabled, skipping save_state for {key}")
            return True

        url = f"{self.base_url}/v1.0/state/{self.state_store}"
        try:
            client = await self._get_client()
            response = await client.post(
                url,
                json=[{"key": key, "value": value}],
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            return True
        except httpx.HTTPStatusError as e:
            logger.error(f"Failed to save state {key}: HTTP {e.response.status_code}")
            return False
        except httpx.RequestError as e:
            logger.error(f"Failed to save state {key}: {e}")
            return False

    async def delete_state(self, key: str) -> bool:
        """
        Delete state by key.

        Args:
            key: State key

        Returns:
            True if successful, False otherwise
        """
        if not self.enabled:
            logger.debug(f"Dapr disabled, skipping delete_state for {key}")
            return True

        url = f"{self.base_url}/v1.0/state/{self.state_store}/{key}"
        try:
            client = await self._get_client()
            response = await client.delete(url)
            response.raise_for_status()
            return True
        except httpx.HTTPStatusError as e:
            logger.error(f"Failed to delete state {key}: HTTP {e.response.status_code}")
            return False
        except httpx.RequestError as e:
            logger.error(f"Failed to delete state {key}: {e}")
            return False

    async def invoke_service(
        self,
        app_id: str,
        method: str,
        data: dict[str, Any] | None = None,
        http_method: str = "POST"
    ) -> dict[str, Any] | None:
        """
        Invoke a method on another Dapr service.

        Args:
            app_id: Target service app ID
            method: Method/endpoint to invoke
            data: Request payload
            http_method: HTTP method (GET, POST, etc.)

        Returns:
            Response data or None on error
        """
        if not self.enabled:
            logger.debug(f"Dapr disabled, skipping invoke {app_id}/{method}")
            return None

        url = f"{self.base_url}/v1.0/invoke/{app_id}/method/{method}"
        try:
            client = await self._get_client()
            if http_method.upper() == "GET":
                response = await client.get(url)
            else:
                response = await client.request(
                    http_method.upper(),
                    url,
                    json=data,
                    headers={"Content-Type": "application/json"}
                )
            response.raise_for_status()
            if response.content:
                return response.json()
            return {}
        except httpx.HTTPStatusError as e:
            logger.error(f"Failed to invoke {app_id}/{method}: HTTP {e.response.status_code}")
            return None
        except httpx.RequestError as e:
            logger.error(f"Failed to invoke {app_id}/{method}: {e}")
            return None


# Singleton instance
dapr_client = DaprClient()
