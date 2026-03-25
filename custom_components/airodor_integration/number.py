"""Number platform for Airodor WiFi Integration."""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

from airodor_wifi_api import airodor
from homeassistant.components.number import (
    NumberDeviceClass,
    NumberEntity,
    NumberEntityDescription,
    NumberMode,
)
from homeassistant.const import UnitOfTime
from homeassistant.util import dt as dt_util

from .entity import AirodorWifiEntity

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import AirodorWifiDataUpdateCoordinator
    from .data import AirodorWifiConfigEntry

ENTITY_DESCRIPTIONS = (
    NumberEntityDescription(
        key="set_timer_a",
        icon="mdi:timer-play",
        translation_key="set_timer_a",
        device_class=NumberDeviceClass.DURATION,
        native_unit_of_measurement=UnitOfTime.HOURS,
        native_min_value=1,
        native_max_value=12,
        native_step=1,
        mode=NumberMode.BOX,
    ),
    NumberEntityDescription(
        key="set_timer_b",
        icon="mdi:timer-play",
        translation_key="set_timer_b",
        device_class=NumberDeviceClass.DURATION,
        native_unit_of_measurement=UnitOfTime.HOURS,
        native_min_value=1,
        native_max_value=12,
        native_step=1,
        mode=NumberMode.BOX,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001 Unused function argument: `hass`
    entry: AirodorWifiConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the number platform."""
    async_add_entities(
        AirodorTimerNumber(
            coordinator=entry.runtime_data.coordinator,
            entity_description=entity_description,
        )
        for entity_description in ENTITY_DESCRIPTIONS
    )


class AirodorTimerNumber(AirodorWifiEntity, NumberEntity):
    """Number entity to set the run timer for an Airodor ventilation group."""

    def __init__(
        self,
        coordinator: AirodorWifiDataUpdateCoordinator,
        entity_description: NumberEntityDescription,
    ) -> None:
        """Initialize the number entity."""
        super().__init__(coordinator, entity_description)
        self._attr_native_value: float | None = entity_description.native_min_value
        self._pending_clear = False

    @property
    def name(self) -> str | None:
        """Return the entity name with configured group name."""
        key = self.entity_description.key
        if key == "set_timer_a":
            group_name = getattr(self.coordinator, "group_a_name", "Group A")
            return f"{group_name} Set Timer"
        if key == "set_timer_b":
            group_name = getattr(self.coordinator, "group_b_name", "Group B")
            return f"{group_name} Set Timer"
        return None

    @property
    def native_value(self) -> float | None:
        """Return the current value (last set timer duration)."""
        return self._attr_native_value

    def _handle_coordinator_update(self) -> None:
        """Handle coordinator updates — reset to min value if pending."""
        if self._pending_clear:
            self._attr_native_value = self.entity_description.native_min_value
            self._pending_clear = False
        super()._handle_coordinator_update()

    async def async_set_native_value(self, value: float) -> None:
        """Set the timer: device will run for the given number of hours."""
        hours = int(value)
        key = self.entity_description.key
        group = (
            airodor.VentilationGroup.A
            if key == "set_timer_a"
            else airodor.VentilationGroup.B
        )

        await self.coordinator.config_entry.runtime_data.client.async_set_timer(
            group=group,
            hours=hours,
        )
        # Record when and what value the timer was set to for accurate countdown
        now = dt_util.utcnow()
        if key == "set_timer_a":
            self.coordinator.timer_a_set_at = now
            self.coordinator.timer_a_set_value = float(hours)
        else:
            self.coordinator.timer_b_set_at = now
            self.coordinator.timer_b_set_value = float(hours)
        # Reset to min value and flag so coordinator callback keeps it reset
        self._attr_native_value = self.entity_description.native_min_value
        self._pending_clear = True
        self.async_write_ha_state()
        await self.coordinator.async_request_refresh()

        # The device needs a few seconds to switch to TIMED_OFF mode.
        # Do a second refresh so the timer sensor picks up the new state.
        await asyncio.sleep(10)
        await self.coordinator.async_request_refresh()
