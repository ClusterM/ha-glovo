"""Device tracker platform for the Glovo integration (courier location)."""

from __future__ import annotations

from typing import Any

from homeassistant.components.device_tracker import SourceType, TrackerEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .coordinator import GlovoConfigEntry, GlovoDataUpdateCoordinator
from .entity import GlovoEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: GlovoConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the Glovo courier tracker."""
    coordinator = entry.runtime_data
    async_add_entities([GlovoCourierTracker(coordinator)])


class GlovoCourierTracker(GlovoEntity, TrackerEntity):
    """Live location of the courier delivering the active order."""

    _attr_translation_key = "courier"
    _attr_icon = "mdi:moped"
    _attr_entity_category = None

    def __init__(self, coordinator: GlovoDataUpdateCoordinator) -> None:
        """Initialize the tracker."""
        super().__init__(coordinator, "courier")

    @property
    def source_type(self) -> SourceType:
        """Return the source type."""
        return SourceType.GPS

    @property
    def latitude(self) -> float | None:
        """Return the courier latitude."""
        value = (self.coordinator.data or {}).get("courier_lat")
        return float(value) if value is not None else None

    @property
    def longitude(self) -> float | None:
        """Return the courier longitude."""
        value = (self.coordinator.data or {}).get("courier_lon")
        return float(value) if value is not None else None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional courier attributes."""
        data = self.coordinator.data or {}
        return {
            "heading": data.get("courier_heading"),
            "courier_name": data.get("courier_name"),
            "courier_count": data.get("courier_count"),
        }
