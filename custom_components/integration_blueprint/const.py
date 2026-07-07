"""Constants for integration_blueprint."""

from logging import Logger, getLogger

from homeassistant.const import CONF_HOST

LOGGER: Logger = getLogger(__package__)

DOMAIN = "integration_blueprint"
ATTRIBUTION = "Data provided by http://jsonplaceholder.typicode.com/"
CONF_DEVICE_HOST = CONF_HOST
DEFAULT_DISPLAY_NAME = "Desk Matrix"
WEBHOOK_ENDPOINT = "/api/integration_blueprint/tap"
