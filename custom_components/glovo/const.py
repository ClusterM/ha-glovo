"""Constants for the Glovo integration."""

from __future__ import annotations

from homeassistant.const import Platform

DOMAIN = "glovo"

# Config entry data keys.
CONF_REFRESH_TOKEN = "refresh_token"
# Full token state as a JSON string produced by the glovo library
# ({"access_token", "refresh_token", "expires_at"}). Persisted in entry.data
# so a fresh access token survives Home Assistant restarts.
CONF_TOKEN = "token"

# Options keys.
CONF_SCAN_INTERVAL = "scan_interval"

DEFAULT_SCAN_INTERVAL = 15
MIN_SCAN_INTERVAL = 5
MAX_SCAN_INTERVAL = 3600

PLATFORMS: list[Platform] = [
    Platform.SENSOR,
    Platform.BINARY_SENSOR,
    Platform.DEVICE_TRACKER,
]
