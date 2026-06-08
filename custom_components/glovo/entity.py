"""Base entity for the Glovo integration."""

from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import GlovoDataUpdateCoordinator


class GlovoEntity(CoordinatorEntity[GlovoDataUpdateCoordinator]):
    """Common base for all Glovo entities."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: GlovoDataUpdateCoordinator, key: str) -> None:
        """Initialize the entity."""
        super().__init__(coordinator)
        entry_id = coordinator.config_entry.entry_id
        self._attr_unique_id = f"{entry_id}_{key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry_id)},
            name="Glovo",
            manufacturer="Glovo",
            model="Customer order",
        )
