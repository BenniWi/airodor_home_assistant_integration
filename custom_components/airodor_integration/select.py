"""Select platform for Airodor WiFi Integration."""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

from airodor_wifi_api import airodor
from homeassistant.components.select import SelectEntity, SelectEntityDescription

from .entity import IntegrationBlueprintEntity

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import BlueprintDataUpdateCoordinator
    from .data import IntegrationBlueprintConfigEntry

# Mapping von VentilationModeSet Enum zu Translations-Keys
MODE_ENUM_TO_KEY = {
    airodor.VentilationModeSet.OFF: "off",
    airodor.VentilationModeSet.ALTERNATING_MIN: "alternating_min",
    airodor.VentilationModeSet.ALTERNATING_MED: "alternating_med",
    airodor.VentilationModeSet.ALTERNATING_MAX: "alternating_max",
    airodor.VentilationModeSet.ONE_DIR_MED: "one_dir_med",
    airodor.VentilationModeSet.ONE_DIR_MAX: "one_dir_max",
    airodor.VentilationModeSet.INSIDE_MED: "inside_med",
    airodor.VentilationModeSet.INSIDE_MAX: "inside_max",
}

# Umgekehrtes Mapping: von Key zu Mode Enum
KEY_TO_MODE_ENUM = {v: k for k, v in MODE_ENUM_TO_KEY.items()}

# Mapping von VentilationModeRead zu VentilationModeSet für Selected Option
# Read-Modi können sich von Set-Modi unterscheiden
READ_TO_SET_MODE = {
    airodor.VentilationModeRead.OFF: airodor.VentilationModeSet.OFF,
    airodor.VentilationModeRead.ALTERNATING_MIN: (
        airodor.VentilationModeSet.ALTERNATING_MIN
    ),
    airodor.VentilationModeRead.ALTERNATING_MED: (
        airodor.VentilationModeSet.ALTERNATING_MED
    ),
    airodor.VentilationModeRead.ALTERNATING_MED_FORCED: (
        airodor.VentilationModeSet.ALTERNATING_MED
    ),
    airodor.VentilationModeRead.ALTERNATING_MAX: (
        airodor.VentilationModeSet.ALTERNATING_MAX
    ),
    airodor.VentilationModeRead.ONE_DIR_MED: (airodor.VentilationModeSet.ONE_DIR_MED),
    airodor.VentilationModeRead.ONE_DIR_MAX: (airodor.VentilationModeSet.ONE_DIR_MAX),
    airodor.VentilationModeRead.INSIDE_MED: (airodor.VentilationModeSet.INSIDE_MED),
    airodor.VentilationModeRead.INSIDE_MAX: (airodor.VentilationModeSet.INSIDE_MAX),
}

ENTITY_DESCRIPTIONS = (
    SelectEntityDescription(
        key="mode_a",
        icon="mdi:fan",
        translation_key="mode_a",
    ),
    SelectEntityDescription(
        key="mode_b",
        icon="mdi:fan",
        translation_key="mode_b",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001 Unused function argument: `hass`
    entry: IntegrationBlueprintConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the select platform."""
    async_add_entities(
        AirodorModeSelect(
            coordinator=entry.runtime_data.coordinator,
            entity_description=entity_description,
        )
        for entity_description in ENTITY_DESCRIPTIONS
    )


class AirodorModeSelect(IntegrationBlueprintEntity, SelectEntity):
    """Select entity for Airodor ventilation mode."""

    def __init__(
        self,
        coordinator: BlueprintDataUpdateCoordinator,
        entity_description: SelectEntityDescription,
    ) -> None:
        """Initialize the select entity."""
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
    def options(self) -> list[str]:
        """Return the available options."""
        return list(MODE_ENUM_TO_KEY.values())

    @property
    def current_option(self) -> str | None:
        """Return the current selected option."""
        data = self.coordinator.data
        if not data:
            return None

        mode_key = self.entity_description.key
        mode = data.get(mode_key)

        if mode is None:
            return None

        # Map read mode to set mode (for finding corresponding option)
        set_mode = READ_TO_SET_MODE.get(mode)
        if set_mode is None:
            return None

        # Get the key for this set mode
        return MODE_ENUM_TO_KEY.get(set_mode)

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        mode_enum = KEY_TO_MODE_ENUM.get(option)

        if mode_enum is None:
            return

        # Determine which group this select entity is for
        mode_key = self.entity_description.key
        if mode_key == "mode_a":
            group = airodor.VentilationGroup.A
        else:
            group = airodor.VentilationGroup.B

        # Set the mode via the API client
        await self.coordinator.config_entry.runtime_data.client.async_set_mode(
            group=group,
            mode=mode_enum,
        )

        # Refresh the coordinator data immediately
        await self.coordinator.async_request_refresh()

        # Wait 10 seconds for the device to update its actual state
        # Then refresh again to get the latest device status
        await asyncio.sleep(10)
        await self.coordinator.async_request_refresh()
