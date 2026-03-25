"""DataUpdateCoordinator for airodor_integration."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import (
    AirodorWifiApiClientAuthenticationError,
    AirodorWifiApiClientError,
)

if TYPE_CHECKING:
    from .data import AirodorWifiConfigEntry


class AirodorWifiDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    config_entry: AirodorWifiConfigEntry
    group_a_name: str = "Group A"
    group_b_name: str = "Group B"

    async def _async_update_data(self) -> Any:
        """Update data via library."""
        try:
            return await self.config_entry.runtime_data.client.async_get_data()
        except AirodorWifiApiClientAuthenticationError as exception:
            raise ConfigEntryAuthFailed(exception) from exception
        except AirodorWifiApiClientError as exception:
            raise UpdateFailed(exception) from exception
