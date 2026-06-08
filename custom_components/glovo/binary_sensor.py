"""Binary sensor platform for the Glovo integration."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .coordinator import GlovoConfigEntry, GlovoDataUpdateCoordinator
from .entity import GlovoEntity


@dataclass(frozen=True, kw_only=True)
class GlovoBinarySensorEntityDescription(BinarySensorEntityDescription):
    """Describes a Glovo binary sensor."""

    value_fn: Callable[[dict[str, Any]], bool | None]


BINARY_SENSORS: tuple[GlovoBinarySensorEntityDescription, ...] = (
    GlovoBinarySensorEntityDescription(
        key="has_active_order",
        translation_key="has_active_order",
        icon="mdi:package-variant",
        value_fn=lambda s: bool(s.get("order_count")),
    ),
    GlovoBinarySensorEntityDescription(
        key="is_late",
        translation_key="is_late",
        device_class=BinarySensorDeviceClass.PROBLEM,
        icon="mdi:clock-alert-outline",
        value_fn=lambda s: s.get("is_late"),
    ),
    GlovoBinarySensorEntityDescription(
        key="chat_available",
        translation_key="chat_available",
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:chat-outline",
        value_fn=lambda s: s.get("chat_available"),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: GlovoConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up Glovo binary sensors."""
    coordinator = entry.runtime_data
    async_add_entities(
        GlovoBinarySensor(coordinator, desc) for desc in BINARY_SENSORS
    )


class GlovoBinarySensor(GlovoEntity, BinarySensorEntity):
    """A Glovo order flag as a binary sensor."""

    entity_description: GlovoBinarySensorEntityDescription

    def __init__(
        self,
        coordinator: GlovoDataUpdateCoordinator,
        description: GlovoBinarySensorEntityDescription,
    ) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator, description.key)
        self.entity_description = description

    @property
    def is_on(self) -> bool | None:
        """Return the current state."""
        return self.entity_description.value_fn(self.coordinator.data or {})
