"""Media player platform for the Desk Matrix display."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any
import json

from homeassistant.components.media_player import (
    MediaPlayerEntity,
    MediaPlayerEntityFeature,
)
from homeassistant.components.media_player.const import MEDIA_TYPE_URL
from homeassistant.const import STATE_OFF, STATE_ON

from .const import DEFAULT_DISPLAY_NAME
from .entity import IntegrationBlueprintEntity

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import BlueprintDataUpdateCoordinator
    from .data import IntegrationBlueprintConfigEntry


async def async_setup_entry(
    hass: HomeAssistant,
    entry: IntegrationBlueprintConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Desk Matrix media player platform."""
    async_add_entities(
        [
            DeskMatrixDisplay(
                coordinator=entry.runtime_data.coordinator,
                device_host=entry.runtime_data.device_host,
                display_name=entry.runtime_data.display_name,
            )
        ]
    )


class DeskMatrixDisplay(IntegrationBlueprintEntity, MediaPlayerEntity):
    """Media player entity that pushes display payloads to a target device."""

    _attr_supported_features = (
        MediaPlayerEntityFeature.TURN_ON
        | MediaPlayerEntityFeature.TURN_OFF
        | MediaPlayerEntityFeature.PLAY_MEDIA
    )

    def __init__(
        self,
        coordinator: BlueprintDataUpdateCoordinator,
        device_host: str | None,
        display_name: str,
    ) -> None:
        """Initialize the Desk Matrix display entity."""
        super().__init__(coordinator)
        self._device_host = device_host
        self._attr_name = f"{display_name} Display"
        self._attr_unique_id = f"{self._attr_unique_id}-display"
        self._attr_available = True
        self._current_media_title = "Desk Matrix ready"
        self._state = STATE_OFF

    @property
    def state(self) -> str:
        """Return the current state of the display."""
        return self._state

    @property
    def media_title(self) -> str | None:
        """Return the current title shown on the display."""
        return self._current_media_title

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on the virtual Desk Matrix display."""
        await self._send_display_payload(
            {
                "command": "wake",
                "message": "Desk Matrix online",
            }
        )
        self._state = STATE_ON

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off the virtual Desk Matrix display."""
        await self._send_display_payload(
            {
                "command": "sleep",
                "message": "Desk Matrix sleeping",
            }
        )
        self._state = STATE_OFF

    async def async_play_media(
        self,
        media_type: str,
        media_id: str,
        **kwargs: Any,
    ) -> None:
        """Send a compact payload to render on the Desk Matrix display."""
        payload = self._build_display_payload(media_type, media_id, kwargs)
        await self._send_display_payload(payload)
        self._current_media_title = media_id or "Desk Matrix payload"
        self._state = STATE_ON

    def _build_display_payload(
        self,
        media_type: str,
        media_id: str,
        extras: dict[str, Any],
    ) -> dict[str, Any]:
        """Build a small JSON payload for the display device."""
        if media_type == MEDIA_TYPE_URL:
            return {
                "command": "render_url",
                "url": media_id,
                "metadata": extras,
            }

        return {
            "command": "render_text",
            "text": media_id,
            "metadata": extras,
        }

    async def _send_display_payload(self, payload: dict[str, Any]) -> None:
        """Send the JSON pixel payload to the local target device."""
        if not self._device_host:
            raise RuntimeError("The Desk Matrix device host is not configured.")

        # Support simple MQTT routing by using a device_host with the
        # mqtt://topic prefix. Otherwise, attempt an HTTP POST to the device.
        if isinstance(self._device_host, str) and self._device_host.startswith(
            "mqtt://"
        ):
            # Format: mqtt://your/topic
            topic = self._device_host[len("mqtt://") :]
            await self.hass.services.async_call(
                "mqtt",
                "publish",
                {
                    "topic": topic,
                    "payload": json.dumps(payload),
                },
            )
            return

        await self.coordinator.config_entry.runtime_data.client.async_send_display_payload(
            self._device_host,
            payload,
        )
