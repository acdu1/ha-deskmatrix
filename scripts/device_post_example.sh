#!/usr/bin/env bash

# Example curl commands to simulate a device receiving payloads and tapping back
# to the integration.

DEVICE_HOST="127.0.0.1:8080"
INTEGRATION_BASE="http://localhost:8123/api/integration_blueprint/tap"

# Render text on the device
curl -X POST -H "Content-Type: application/json" \
  -d '{ "command": "render_text", "text": "Hello Desk", "metadata": {} }' \
  http://$DEVICE_HOST/display

# Wake the device
curl -X POST -H "Content-Type: application/json" \
  -d '{ "command": "wake", "message": "Desk Matrix online" }' \
  http://$DEVICE_HOST/display

# Simulate a tap on the device that triggers a turn_on service
curl -X POST -H "Content-Type: application/json" \
  -d '{ "action": "turn_on", "entity_id": "switch.desk_lamp" }' \
  $INTEGRATION_BASE

# Simulate a notify action
curl -X POST -H "Content-Type: application/json" \
  -d '{ "action": "notify", "entity_id": "notify.mobile_app", "message": "Button pressed" }' \
  $INTEGRATION_BASE
