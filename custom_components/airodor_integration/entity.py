"""BlueprintEntity class."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import ATTRIBUTION, CONF_AREA, CONF_DEVICE_NAME, DEFAULT_DEVICE_NAME
from .coordinator import BlueprintDataUpdateCoordinator

if TYPE_CHECKING:
    from homeassistant.components.select import SelectEntityDescription
    from homeassistant.components.sensor import SensorEntityDescription


class IntegrationBlueprintEntity(CoordinatorEntity[BlueprintDataUpdateCoordinator]):
    """BlueprintEntity class."""

    _attr_attribution = ATTRIBUTION
    entity_description: SensorEntityDescription | SelectEntityDescription

    def __init__(
        self,
        coordinator: BlueprintDataUpdateCoordinator,
        entity_description: SensorEntityDescription
        | SelectEntityDescription
        | None = None,
    ) -> None:
        """Initialize."""
        super().__init__(coordinator)

        if entity_description:
            self.entity_description = entity_description
            # Generate unique_id from entry_id and entity_description key
            self._attr_unique_id = (
                f"{coordinator.config_entry.entry_id}_{entity_description.key}"
            )
        else:
            # Fallback to entry_id if no entity_description provided
            self._attr_unique_id = coordinator.config_entry.entry_id

        self._attr_device_info = DeviceInfo(
            identifiers={
                (
                    coordinator.config_entry.domain,
                    coordinator.config_entry.entry_id,
                ),
            },
            name=coordinator.config_entry.data.get(
                CONF_DEVICE_NAME, DEFAULT_DEVICE_NAME
            ),
            manufacturer="Limodor",
            model="Airodor WiFi",
            suggested_area=coordinator.config_entry.data.get(CONF_AREA) or None,
        )
