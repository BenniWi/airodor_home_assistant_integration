"""
Custom integration to integrate Airodor WiFi with Home Assistant.

For more details about this integration, please refer to
https://github.com/BenniWi/airodor_home_assistant_integration
"""

from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING

from homeassistant.const import Platform
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.loader import async_get_loaded_integration

from .api import IntegrationBlueprintApiClient
from .const import (
    CONF_GROUP_A_NAME,
    CONF_GROUP_B_NAME,
    CONF_IP_ADDRESS,
    CONF_UPDATE_INTERVAL,
    DEFAULT_GROUP_A_NAME,
    DEFAULT_GROUP_B_NAME,
    DEFAULT_UPDATE_INTERVAL,
    DOMAIN,
    LOGGER,
)
from .coordinator import BlueprintDataUpdateCoordinator
from .data import IntegrationBlueprintData

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant, ServiceCall

    from .data import IntegrationBlueprintConfigEntry

PLATFORMS: list[Platform] = [
    Platform.BUTTON,
    Platform.SENSOR,
    Platform.SELECT,
]


# https://developers.home-assistant.io/docs/config_entries_index/#setting-up-an-entry
async def async_setup_entry(
    hass: HomeAssistant,
    entry: IntegrationBlueprintConfigEntry,
) -> bool:
    """Set up this integration using UI."""
    update_interval_minutes = entry.data.get(
        CONF_UPDATE_INTERVAL,
        DEFAULT_UPDATE_INTERVAL,
    )
    group_a_name = entry.data.get(CONF_GROUP_A_NAME, DEFAULT_GROUP_A_NAME)
    group_b_name = entry.data.get(CONF_GROUP_B_NAME, DEFAULT_GROUP_B_NAME)

    coordinator = BlueprintDataUpdateCoordinator(
        hass=hass,
        logger=LOGGER,
        name=DOMAIN,
        update_interval=timedelta(minutes=update_interval_minutes),
    )
    coordinator.group_a_name = group_a_name
    coordinator.group_b_name = group_b_name
    entry.runtime_data = IntegrationBlueprintData(
        client=IntegrationBlueprintApiClient(
            ip_address=entry.data[CONF_IP_ADDRESS],
            session=async_get_clientsession(hass),
        ),
        integration=async_get_loaded_integration(hass, entry.domain),
        coordinator=coordinator,
    )

    # https://developers.home-assistant.io/docs/integration_fetching_data#coordinated-single-api-poll-for-data-for-all-entities
    await coordinator.async_config_entry_first_refresh()

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    # Register refresh service
    async def async_refresh_data(call: ServiceCall) -> None:  # noqa: ARG001
        """Refresh data for this integration."""
        await coordinator.async_request_refresh()

    hass.services.async_register(
        DOMAIN,
        "refresh_data",
        async_refresh_data,
    )

    return True


async def async_unload_entry(
    hass: HomeAssistant,
    entry: IntegrationBlueprintConfigEntry,
) -> bool:
    """Handle removal of an entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def async_reload_entry(
    hass: HomeAssistant,
    entry: IntegrationBlueprintConfigEntry,
) -> None:
    """Reload config entry."""
    await hass.config_entries.async_reload(entry.entry_id)
