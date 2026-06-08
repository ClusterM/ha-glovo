"""DataUpdateCoordinator for the Glovo integration."""

from __future__ import annotations

import json
import logging
from datetime import timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from . import glovo
from .const import (
    CONF_SCAN_INTERVAL,
    CONF_TOKEN,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    FIXTURES_REL_PATH,
)

_LOGGER = logging.getLogger(__name__)

type GlovoConfigEntry = ConfigEntry[GlovoDataUpdateCoordinator]


class GlovoDataUpdateCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Poll the Glovo API for the last active order summary."""

    config_entry: GlovoConfigEntry

    def __init__(self, hass: HomeAssistant, entry: GlovoConfigEntry) -> None:
        """Initialize the coordinator."""
        self._base_interval = timedelta(
            seconds=entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
        )
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            config_entry=entry,
            update_interval=self._base_interval,
        )

    async def _async_update_data(self) -> dict[str, Any]:
        fixtures_dir = self.hass.config.path(FIXTURES_REL_PATH)
        if glovo.fixtures_available(fixtures_dir):
            _LOGGER.warning(
                "Serving Glovo data from local fixtures in %s (API disabled)",
                fixtures_dir,
            )
            try:
                summary = await self.hass.async_add_executor_job(
                    glovo.get_last_active_order_summary_from_fixtures, fixtures_dir
                )
            except (OSError, json.JSONDecodeError, RuntimeError) as err:
                raise UpdateFailed(f"Invalid Glovo fixture files: {err}") from err
        else:
            token_json = self.config_entry.data[CONF_TOKEN]
            try:
                summary, new_token = await self.hass.async_add_executor_job(
                    glovo.get_last_active_order_summary, token_json
                )
            except glovo.GlovoApiError as err:
                if err.status in (401, 403):
                    raise ConfigEntryAuthFailed(
                        "Glovo token rejected, re-authentication required"
                    ) from err
                raise UpdateFailed(f"Glovo API error: {err}") from err
            except RuntimeError as err:
                # Raised when the refresh token is missing/invalid.
                raise ConfigEntryAuthFailed(str(err)) from err

            if new_token != token_json:
                self.hass.config_entries.async_update_entry(
                    self.config_entry,
                    data={**self.config_entry.data, CONF_TOKEN: new_token},
                )

        self._apply_dynamic_interval(summary)
        return summary

    def _apply_dynamic_interval(self, summary: dict[str, Any]) -> None:
        """Use the API-recommended poll interval while an order is active."""
        poll_interval = summary.get("poll_interval_sec")
        if summary.get("active") and poll_interval:
            self.update_interval = timedelta(seconds=float(poll_interval))
        else:
            self.update_interval = self._base_interval
