"""Button platform for Airodor WiFi Integration."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.button import ButtonEntity, ButtonEntityDescription

from .entity import AirodorWifiEntity

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import AirodorWifiDataUpdateCoordinator
    from .data import AirodorWifiConfigEntry


ENTITY_DESCRIPTION = ButtonEntityDescription(
    key="refresh",
    icon="mdi:refresh",
    name="Aktualisieren",
)


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001
    entry: AirodorWifiConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the button platform."""
    async_add_entities(
        [
            AirodorRefreshButton(
                coordinator=entry.runtime_data.coordinator,
                entity_description=ENTITY_DESCRIPTION,
            )
        ]
    )


class AirodorRefreshButton(AirodorWifiEntity, ButtonEntity):
    """Button to trigger a manual data refresh."""

    def __init__(
        self,
        coordinator: AirodorWifiDataUpdateCoordinator,
        entity_description: ButtonEntityDescription,
    ) -> None:
        """Initialize the button."""
        super().__init__(coordinator, entity_description)

    async def async_press(self) -> None:
        """Handle the button press - trigger data refresh."""
        await self.coordinator.async_request_refresh()
