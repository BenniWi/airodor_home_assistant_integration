"""API Client for Airodor WiFi Integration."""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Any

from airodor_wifi_api import airodor

if TYPE_CHECKING:
    from aiohttp import ClientSession


class AirodorWifiApiClientError(Exception):
    """Exception to indicate a general API error."""


class AirodorWifiApiClientCommunicationError(
    AirodorWifiApiClientError,
):
    """Exception to indicate a communication error."""


class AirodorWifiApiClientAuthenticationError(
    AirodorWifiApiClientError,
):
    """Exception to indicate an authentication error."""


class AirodorWifiApiClient:
    """API Client for Airodor WiFi."""

    def __init__(
        self,
        host: str,
        port: int,
        session: ClientSession,
    ) -> None:
        """
        Initialize API Client.

        Args:
            host: Hostname or IP address of the Airodor WiFi device
            port: TCP port of the device (default 80)
            session: aiohttp ClientSession

        """
        self._host = host
        self._port = port
        self._session = session

    async def async_get_data(self) -> dict[str, Any]:
        """
        Get current data from the device.

        Returns:
            Dictionary with current ventilation status

        """
        try:
            # Get mode for both groups first
            mode_a = await self._async_get_mode(airodor.VentilationGroup.A)
            mode_b = await self._async_get_mode(airodor.VentilationGroup.B)
            # Only fetch timer when the device is actually in TIMED_OFF mode,
            # matching the reference web app behaviour and avoiding unneeded requests.
            timer_a = (
                await self._async_get_timer(airodor.VentilationGroup.A)
                if mode_a
                in (
                    airodor.VentilationModeRead.TIMED_OFF,
                    airodor.VentilationModeRead.TIMED_OFF_UNKNOWN,
                )
                else None
            )
            timer_b = (
                await self._async_get_timer(airodor.VentilationGroup.B)
                if mode_b
                in (
                    airodor.VentilationModeRead.TIMED_OFF,
                    airodor.VentilationModeRead.TIMED_OFF_UNKNOWN,
                )
                else None
            )
        except Exception as exception:
            msg = f"Error fetching data from Airodor device - {exception}"
            raise AirodorWifiApiClientCommunicationError(msg) from exception
        else:
            return {
                "mode_a": mode_a,
                "mode_b": mode_b,
                "timer_a": timer_a,
                "timer_b": timer_b,
            }

    async def async_set_mode(
        self,
        group: airodor.VentilationGroup,
        mode: airodor.VentilationModeSet,
    ) -> bool:
        """
        Set ventilation mode.

        Args:
            group: Ventilation group (A or B)
            mode: Mode to set

        Returns:
            True if successful

        """
        try:
            result = await self._async_set_mode(group, mode)
        except Exception as exception:
            msg = f"Error setting mode on Airodor device - {exception}"
            raise AirodorWifiApiClientCommunicationError(msg) from exception
        else:
            return result

    async def _async_get_mode(
        self,
        group: airodor.VentilationGroup,
    ) -> airodor.VentilationModeRead:
        """Get current mode for a group."""
        try:
            return await asyncio.to_thread(
                airodor.get_mode, self._host, self._port, group
            )
        except Exception as exception:
            msg = f"Error getting mode from {self._host}:{self._port} - {exception}"
            raise AirodorWifiApiClientCommunicationError(msg) from exception

    async def _async_set_mode(
        self,
        group: airodor.VentilationGroup,
        mode: airodor.VentilationModeSet,
    ) -> bool:
        """Set mode for a group."""
        try:
            return await asyncio.to_thread(
                airodor.set_mode, self._host, self._port, group, mode
            )
        except Exception as exception:
            msg = f"Error setting mode on {self._host}:{self._port} - {exception}"
            raise AirodorWifiApiClientCommunicationError(msg) from exception

    async def _async_get_timer(
        self,
        group: airodor.VentilationGroup,
    ) -> int | None:
        """Get timer value for a group."""
        try:
            return await asyncio.to_thread(
                airodor.get_timer, self._host, self._port, group
            )
        except Exception as exception:
            msg = f"Error getting timer from {self._host}:{self._port} - {exception}"
            raise AirodorWifiApiClientCommunicationError(msg) from exception

    async def async_set_timer(
        self,
        group: airodor.VentilationGroup,
        hours: int,
    ) -> bool:
        """
        Set the run timer for a ventilation group.

        Args:
            group: Ventilation group (A or B)
            hours: Number of hours the device should run before turning off

        Returns:
            True if successful

        """
        try:
            return await asyncio.to_thread(
                airodor.set_timer, self._host, self._port, group, hours
            )
        except Exception as exception:
            msg = f"Error setting timer on Airodor device - {exception}"
            raise AirodorWifiApiClientCommunicationError(msg) from exception
