# Desk Matrix Home Assistant Integration

A custom Home Assistant integration that turns an old tablet, Kindle, or DIY
ESP32 display into a dedicated desk-side appliance controller.

This integration exposes a `media_player` entity that pushes compact JSON
payloads to a local display device and a webhook endpoint for tap/callback
actions from the screen.

## Overview

- The custom integration code lives in `custom_components/integration_blueprint/`.
- It creates a physical desk display controller entity in Home Assistant.
- The display can receive payloads over HTTP or via MQTT routing.
- Tap actions from the screen are handled through a local webhook and can
  instantly trigger Home Assistant services.

## Install

1. Copy `custom_components/integration_blueprint/` into your Home Assistant
   `config/custom_components/` directory.
2. Restart Home Assistant.
3. Configure the integration from the UI and provide the target display host.
4. The integration creates a `media_player` entity for the desk display.

## Features

- `TURN_ON` / `TURN_OFF` support for wake/sleep display commands.
- `PLAY_MEDIA` support for sending text or URL rendering payloads.
- Optional MQTT routing when `device_host` starts with `mqtt://`.
- Local webhook endpoint at `/api/integration_blueprint/tap` for handling screen taps.

## Device payloads

The integration sends JSON payloads to the target device. By default it POSTs to
`http://<device_host>/display`.

Render text:

```json
{ "command": "render_text", "text": "Hello Desk", "metadata": {} }
```

Render a URL:

```json
{ "command": "render_url", "url": "http://example.local/image.png", "metadata": {} }
```

Wake / Sleep commands:

```json
{ "command": "wake", "message": "Desk Matrix online" }
{ "command": "sleep", "message": "Desk Matrix sleeping" }
```

## Tap webhook

Devices can POST tap actions to the local webhook:

`/api/integration_blueprint/tap`

Example switch action:

```json
{ "action": "turn_on", "entity_id": "switch.desk_lamp" }
```

Example notify action:

```json
{ "action": "notify", "entity_id": "notify.mobile_app", "message": "Button pressed" }
```

## Notes

- This integration is designed for simple desk displays and low-power screens.
- It uses small deterministic JSON payloads rather than a full dashboard.
- Use a local display script or app that can render these commands and send
  tap callbacks back to Home Assistant.
