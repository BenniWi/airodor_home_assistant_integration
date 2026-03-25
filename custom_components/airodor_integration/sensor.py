"""Sensor platform for Airodor WiFi Integration."""

from __future__ import annotations

from typing import TYPE_CHECKING

from airodor_wifi_api import airodor
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
)

from .entity import AirodorWifiEntity

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import AirodorWifiDataUpdateCoordinator
    from .data import AirodorWifiConfigEntry

# Mapping from VentilationModeRead to option keys (same keys as select/translations)
MODE_READ_TO_KEY = {
    airodor.VentilationModeRead.OFF: "off",
    airodor.VentilationModeRead.ALTERNATING_MIN: "alternating_min",
    airodor.VentilationModeRead.ALTERNATING_MED: "alternating_med",
    airodor.VentilationModeRead.ALTERNATING_MED_FORCED: "alternating_med_forced",
    airodor.VentilationModeRead.ALTERNATING_MAX: "alternating_max",
    airodor.VentilationModeRead.ONE_DIR_MED: "one_dir_med",
    airodor.VentilationModeRead.ONE_DIR_MAX: "one_dir_max",
    airodor.VentilationModeRead.INSIDE_MED: "inside_med",
    airodor.VentilationModeRead.INSIDE_MAX: "inside_max",
    airodor.VentilationModeRead.TIMED_OFF: "timed_off",
    airodor.VentilationModeRead.UNKNOWN: "unknown",
}

_SENSOR_OPTIONS = [
    "off",
    "alternating_min",
    "alternating_med",
    "alternating_med_forced",
    "alternating_max",
    "one_dir_med",
    "one_dir_max",
    "inside_med",
    "inside_max",
    "timed_off",
    "unknown",
]

ENTITY_DESCRIPTIONS = (
    SensorEntityDescription(
        key="mode_a",
        icon="mdi:fan",
        translation_key="mode_a",
        device_class=SensorDeviceClass.ENUM,
        options=_SENSOR_OPTIONS,
    ),
    SensorEntityDescription(
        key="mode_b",
        icon="mdi:fan",
        translation_key="mode_b",
        device_class=SensorDeviceClass.ENUM,
        options=_SENSOR_OPTIONS,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001 Unused function argument: `hass`
    entry: AirodorWifiConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    async_add_entities(
        AirodorModeSensor(
            coordinator=entry.runtime_data.coordinator,
            entity_description=entity_description,
        )
        for entity_description in ENTITY_DESCRIPTIONS
    )


class AirodorModeSensor(AirodorWifiEntity, SensorEntity):
    """Sensor for Airodor ventilation mode."""

    def __init__(
        self,
        coordinator: AirodorWifiDataUpdateCoordinator,
        entity_description: SensorEntityDescription,
    ) -> None:
        """Initialize the sensor class."""
        super().__init__(coordinator, entity_description)

    @property
    def name(self) -> str | None:
        """Return the entity name with configured group name."""
        mode_key = self.entity_description.key
        if mode_key == "mode_a":
            group_name = getattr(self.coordinator, "group_a_name", "Group A")
            return f"{group_name} Ventilation Mode"
        if mode_key == "mode_b":
            group_name = getattr(self.coordinator, "group_b_name", "Group B")
            return f"{group_name} Ventilation Mode"
        return None

    @property
    def native_value(self) -> str | None:
        """Return the native value of the sensor."""
        data = self.coordinator.data
        if not data:
            return None

        mode_key = self.entity_description.key
        mode = data.get(mode_key)

        if mode is None:
            return None

        return MODE_READ_TO_KEY.get(mode)
