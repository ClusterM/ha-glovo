"""Sensor platform for the Glovo integration."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
)
from homeassistant.const import PERCENTAGE, EntityCategory, UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import glovo
from .coordinator import GlovoConfigEntry, GlovoDataUpdateCoordinator
from .entity import GlovoEntity


@dataclass(frozen=True, kw_only=True)
class GlovoSensorEntityDescription(SensorEntityDescription):
    """Describes a Glovo sensor."""

    value_fn: Callable[[dict[str, Any]], Any]
    primary: bool = False


def _eta_window(summary: dict[str, Any]) -> str | None:
    if summary.get("eta_format") != "timestamp":
        return None
    low, high = summary.get("eta_min"), summary.get("eta_max")
    if not low or not high:
        return None
    return f"{low} – {high}"


SENSORS: tuple[GlovoSensorEntityDescription, ...] = (
    GlovoSensorEntityDescription(
        key="overall_status",
        translation_key="overall_status",
        device_class=SensorDeviceClass.ENUM,
        options=list(glovo.ENUMS["overall.status"].keys()),
        icon="mdi:moped",
        value_fn=lambda s: s.get("overall_status"),
        primary=True,
    ),
    GlovoSensorEntityDescription(
        key="step",
        translation_key="step",
        device_class=SensorDeviceClass.ENUM,
        options=list(glovo.ENUMS["tracking.step"].keys()),
        icon="mdi:progress-clock",
        value_fn=lambda s: s.get("step"),
    ),
    GlovoSensorEntityDescription(
        key="store_name",
        translation_key="store_name",
        icon="mdi:storefront",
        value_fn=lambda s: s.get("store_name"),
    ),
    GlovoSensorEntityDescription(
        key="order_count",
        translation_key="order_count",
        icon="mdi:format-list-numbered",
        value_fn=lambda s: s.get("order_count"),
    ),
    GlovoSensorEntityDescription(
        key="courier_name",
        translation_key="courier_name",
        icon="mdi:account",
        value_fn=lambda s: s.get("courier_name"),
    ),
    GlovoSensorEntityDescription(
        key="courier_status",
        translation_key="courier_status",
        device_class=SensorDeviceClass.ENUM,
        options=list(glovo.ENUMS["tracking.courierStatus"].keys()),
        icon="mdi:bike-fast",
        value_fn=lambda s: s.get("courier_status"),
    ),
    GlovoSensorEntityDescription(
        key="partner_status",
        translation_key="partner_status",
        device_class=SensorDeviceClass.ENUM,
        options=list(glovo.ENUMS["tracking.partnerStatus"].keys()),
        icon="mdi:chef-hat",
        value_fn=lambda s: s.get("partner_status"),
    ),
    GlovoSensorEntityDescription(
        key="progress_percent",
        translation_key="progress_percent",
        native_unit_of_measurement=PERCENTAGE,
        icon="mdi:percent",
        value_fn=lambda s: s.get("progress_percent"),
    ),
    GlovoSensorEntityDescription(
        key="eta_minutes_left",
        translation_key="eta_minutes_left",
        device_class=SensorDeviceClass.DURATION,
        native_unit_of_measurement=UnitOfTime.MINUTES,
        icon="mdi:clock-end",
        value_fn=lambda s: s.get("eta_minutes_left"),
    ),
    GlovoSensorEntityDescription(
        key="eta_text",
        translation_key="eta_text",
        icon="mdi:clock-outline",
        value_fn=lambda s: s.get("eta_text"),
    ),
    GlovoSensorEntityDescription(
        key="eta_window",
        translation_key="eta_window",
        icon="mdi:clock-time-four-outline",
        value_fn=_eta_window,
    ),
    GlovoSensorEntityDescription(
        key="poll_interval_sec",
        translation_key="poll_interval_sec",
        device_class=SensorDeviceClass.DURATION,
        native_unit_of_measurement=UnitOfTime.SECONDS,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
        icon="mdi:timer-sync-outline",
        value_fn=lambda s: s.get("poll_interval_sec"),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: GlovoConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up Glovo sensors."""
    coordinator = entry.runtime_data
    async_add_entities(GlovoSensor(coordinator, desc) for desc in SENSORS)


class GlovoSensor(GlovoEntity, SensorEntity):
    """A single Glovo order field as a sensor."""

    entity_description: GlovoSensorEntityDescription

    def __init__(
        self,
        coordinator: GlovoDataUpdateCoordinator,
        description: GlovoSensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, description.key)
        self.entity_description = description

    @property
    def native_value(self) -> Any:
        """Return the current value."""
        return self.entity_description.value_fn(self.coordinator.data or {})

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Expose the full summary on the primary status sensor."""
        if not self.entity_description.primary:
            return None
        return dict(self.coordinator.data or {})
