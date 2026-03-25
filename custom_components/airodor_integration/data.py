"""Custom types for airodor_integration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.loader import Integration

    from .api import AirodorWifiApiClient
    from .coordinator import AirodorWifiDataUpdateCoordinator


type AirodorWifiConfigEntry = ConfigEntry[AirodorWifiData]


@dataclass
class AirodorWifiData:
    """Data for the Airodor Wifi integration."""

    client: AirodorWifiApiClient
    coordinator: AirodorWifiDataUpdateCoordinator
    integration: Integration
