"""Sensor platform for Airodor WiFi Integration."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING

from airodor_wifi_api import airodor
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
)
from homeassistant.util import dt as dt_util

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
    airodor.VentilationModeRead.TIMED_OFF_UNKNOWN: "timed_off",
    airodor.VentilationModeRead.UNKNOWN: "timed_off",
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
]

MODE_ENTITY_DESCRIPTIONS = (
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

TIMER_ENTITY_DESCRIPTIONS = (
    SensorEntityDescription(
        key="timer_a",
        icon="mdi:clock-end",
        translation_key="timer_a",
    ),
    SensorEntityDescription(
        key="timer_b",
        icon="mdi:clock-end",
        translation_key="timer_b",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001 Unused function argument: `hass`
    entry: AirodorWifiConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    coordinator = entry.runtime_data.coordinator
    entities: list[SensorEntity] = [
        AirodorModeSensor(coordinator=coordinator, entity_description=desc)
        for desc in MODE_ENTITY_DESCRIPTIONS
    ]
    entities += [
        AirodorTimerSensor(coordinator=coordinator, entity_description=desc)
        for desc in TIMER_ENTITY_DESCRIPTIONS
    ]
    async_add_entities(entities)


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


class AirodorTimerSensor(AirodorWifiEntity, SensorEntity):
    """Sensor for Airodor off-timer remaining duration."""

    def __init__(
        self,
        coordinator: AirodorWifiDataUpdateCoordinator,
        entity_description: SensorEntityDescription,
    ) -> None:
        """Initialize the timer sensor."""
        super().__init__(coordinator, entity_description)

    @property
    def name(self) -> str | None:
        """Return the entity name with configured group name."""
        timer_key = self.entity_description.key
        if timer_key == "timer_a":
            group_name = getattr(self.coordinator, "group_a_name", "Group A")
            return f"{group_name} Off-Timer"
        if timer_key == "timer_b":
            group_name = getattr(self.coordinator, "group_b_name", "Group B")
            return f"{group_name} Off-Timer"
        return None

    @property
    def native_value(self) -> str | None:
        """Return the time at which the timer expires as a local HH:MM string."""
        data = self.coordinator.data
        if not data:
            return None

        timer_key = self.entity_description.key
        # Determine which mode and timer belong to this group
        mode_key = "mode_a" if timer_key == "timer_a" else "mode_b"
        mode = data.get(mode_key)

        # Timer value is only meaningful when the device is in TIMED_OFF mode
        if mode not in (
            airodor.VentilationModeRead.TIMED_OFF,
            airodor.VentilationModeRead.TIMED_OFF_UNKNOWN,
        ):
            return None

        # Check if we have HA-side tracking data (timer was set via this instance)
        if timer_key == "timer_a":
            set_at = getattr(self.coordinator, "timer_a_set_at", None)
            set_value = getattr(self.coordinator, "timer_a_set_value", None)
        else:
            set_at = getattr(self.coordinator, "timer_b_set_at", None)
            set_value = getattr(self.coordinator, "timer_b_set_value", None)

        if set_at is not None and set_value is not None:
            # Accurate countdown from HA-side tracking data
            elapsed_hours = (datetime.now(tz=UTC) - set_at).total_seconds() / 3600
            remaining = max(0.0, set_value - elapsed_hours)
            expiry = dt_util.now() + timedelta(hours=remaining)
            return expiry.strftime("%H:%M")

        # Fallback: timer was set externally — use device value as upper bound
        timer_value = data.get(timer_key)
        if timer_value is None:
            return None

        expiry_upper = dt_util.now() + timedelta(hours=timer_value)
        return f"max. {expiry_upper.strftime('%H:%M')}"
