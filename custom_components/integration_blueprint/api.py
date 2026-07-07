"""Sample API Client."""

from __future__ import annotations

import socket
from typing import Any

import aiohttp
import async_timeout


class IntegrationBlueprintApiClientError(Exception):
    """Exception to indicate a general API error."""


class IntegrationBlueprintApiClientCommunicationError(
    IntegrationBlueprintApiClientError,
):
    """Exception to indicate a communication error."""


class IntegrationBlueprintApiClientAuthenticationError(
    IntegrationBlueprintApiClientError,
):
    """Exception to indicate an authentication error."""


def _verify_response_or_raise(response: aiohttp.ClientResponse) -> None:
    """Verify that the response is valid."""
    if response.status in (401, 403):
        msg = "Invalid credentials"
        raise IntegrationBlueprintApiClientAuthenticationError(
            msg,
        )
    response.raise_for_status()


class IntegrationBlueprintApiClient:
    """Sample API Client."""

    def __init__(
        self,
        username: str,
        password: str,
        session: aiohttp.ClientSession,
    ) -> None:
        """Sample API Client."""
        self._username = username
        self._password = password
        self._session = session

    async def async_get_data(self) -> Any:
        """Get data from the API."""
        return await self._api_wrapper(
            method="get",
            url="https://jsonplaceholder.typicode.com/posts/1",
        )

    async def async_set_title(self, value: str) -> Any:
        """Get data from the API."""
        return await self._api_wrapper(
            method="patch",
            url="https://jsonplaceholder.typicode.com/posts/1",
            data={"title": value},
            headers={"Content-type": "application/json; charset=UTF-8"},
        )

    async def _api_wrapper(
        self,
        method: str,
        url: str,
        data: dict | None = None,
        headers: dict | None = None,
    ) -> Any:
        """Get information from the API."""
        try:
            async with async_timeout.timeout(10):
                response = await self._session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=data,
                )
                _verify_response_or_raise(response)
                return await response.json()

        except TimeoutError as exception:
            msg = f"Timeout error fetching information - {exception}"
            raise IntegrationBlueprintApiClientCommunicationError(
                msg,
            ) from exception
        except (aiohttp.ClientError, socket.gaierror) as exception:
            msg = f"Error fetching information - {exception}"
            raise IntegrationBlueprintApiClientCommunicationError(
                msg,
            ) from exception
        except Exception as exception:  # pylint: disable=broad-except
            msg = f"Something really wrong happened! - {exception}"
            raise IntegrationBlueprintApiClientError(
                msg,
            ) from exception

    async def async_send_display_payload(self, device_host: str, payload: dict) -> None:
        """Send a JSON payload to a simple local display device over HTTP.

        The device_host can be a host:port pair (e.g. "192.168.1.42:8080") or a
        fully qualified URL (e.g. "http://192.168.1.42:8080/display").
        """
        # Normalize to a URL if a bare host/host:port is provided.
        if device_host.startswith("http://") or device_host.startswith("https://"):
            url = device_host
        else:
            url = f"http://{device_host}/display"

        try:
            async with async_timeout.timeout(10):
                response = await self._session.post(url, json=payload)
                _verify_response_or_raise(response)
        except TimeoutError as exception:
            msg = f"Timeout when sending display payload - {exception}"
            raise IntegrationBlueprintApiClientCommunicationError(msg) from exception
        except (aiohttp.ClientError, socket.gaierror) as exception:
            msg = f"Error sending display payload - {exception}"
            raise IntegrationBlueprintApiClientCommunicationError(msg) from exception
