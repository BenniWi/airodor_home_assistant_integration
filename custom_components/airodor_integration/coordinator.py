"""DataUpdateCoordinator for airodor_integration."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

from airodor_wifi_api import airodor
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
    last_data_time: datetime | None = None
    # Tracks when each timer was set and with which value (for accurate countdown)
    timer_a_set_at: datetime | None = None
    timer_a_set_value: float | None = None
    timer_b_set_at: datetime | None = None
    timer_b_set_value: float | None = None

    async def _async_update_data(self) -> Any:
        """Update data via library."""
        try:
            data = await self.config_entry.runtime_data.client.async_get_data()
        except AirodorWifiApiClientAuthenticationError as exception:
            raise ConfigEntryAuthFailed(exception) from exception
        except AirodorWifiApiClientError as exception:
            raise UpdateFailed(exception) from exception
        else:
            self.last_data_time = datetime.now(tz=UTC)
            # Clear in-memory timer tracking when the group is no longer in
            # TIMED_OFF mode AND the timer data from the device confirms it
            # (timer_value is None because we don't fetch it for non-TIMED_OFF).
            # Only clear if set_at is old enough (>30s) to avoid a race where
            # the device hasn't switched to TIMED_OFF yet right after setting.
            now = datetime.now(tz=UTC)
            if data.get("mode_a") not in (
                airodor.VentilationModeRead.TIMED_OFF,
                airodor.VentilationModeRead.TIMED_OFF_UNKNOWN,
            ):
                if (
                    self.timer_a_set_at is None
                    or (now - self.timer_a_set_at).total_seconds() > 30
                ):
                    self.timer_a_set_at = None
                    self.timer_a_set_value = None
            if data.get("mode_b") not in (
                airodor.VentilationModeRead.TIMED_OFF,
                airodor.VentilationModeRead.TIMED_OFF_UNKNOWN,
            ):
                if (
                    self.timer_b_set_at is None
                    or (now - self.timer_b_set_at).total_seconds() > 30
                ):
                    self.timer_b_set_at = None
                    self.timer_b_set_value = None
            return data
