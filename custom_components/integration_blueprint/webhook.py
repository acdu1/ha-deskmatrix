"""HTTP endpoint for Desk Matrix tap actions."""

from __future__ import annotations

from typing import Any

from aiohttp import web
from homeassistant.components.http import HomeAssistantView
from homeassistant.const import HTTP_BAD_REQUEST

from .const import DOMAIN


class DeskMatrixTapView(HomeAssistantView):
    """Provide a local endpoint for tappable desk display actions."""

    url = "/api/integration_blueprint/tap"
    name = "api:integration_blueprint:tap"
    requires_auth = False

    def __init__(self, hass) -> None:
        self.hass = hass

    async def post(self, request: web.Request) -> web.Response:
        """Handle POST requests from the target display."""
        try:
            request_data = await request.json()
        except ValueError:
            return self.json({"error": "Invalid JSON body"}, HTTP_BAD_REQUEST)

        action = (request_data.get("action") or "").lower()
        entity_id = request_data.get("entity_id")
        extra_data = request_data.get("data", {})

        if not action or not entity_id:
            return self.json(
                {"error": "Request must include action and entity_id."},
                HTTP_BAD_REQUEST,
            )

        service_domain = "homeassistant"
        service_name = action
        service_data: dict[str, Any] = {"entity_id": entity_id}

        if action == "notify":
            service_domain = "notify"
            service_name = "notify"
            service_data["message"] = request_data.get(
                "message", "Desk Matrix tap received"
            )
        elif action not in {"turn_on", "turn_off", "toggle"}:
            return self.json(
                {"error": f"Unsupported action '{action}'."},
                HTTP_BAD_REQUEST,
            )

        if isinstance(extra_data, dict):
            service_data.update(extra_data)

        await self.hass.services.async_call(
            service_domain,
            service_name,
            service_data,
            blocking=True,
        )

        return self.json(
            {
                "success": True,
                "action": action,
                "entity_id": entity_id,
            }
        )
