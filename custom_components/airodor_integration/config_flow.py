"""Adds config flow for Airodor Integration."""

from __future__ import annotations

import ipaddress

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers import selector
from homeassistant.helpers.aiohttp_client import async_create_clientsession
from homeassistant.loader import async_get_loaded_integration

from .api import (
    AirodorWifiApiClient,
    AirodorWifiApiClientCommunicationError,
    AirodorWifiApiClientError,
)
from .const import (
    CONF_AREA,
    CONF_DEVICE_NAME,
    CONF_GROUP_A_NAME,
    CONF_GROUP_B_NAME,
    CONF_IP_ADDRESS,
    CONF_UPDATE_INTERVAL,
    DEFAULT_DEVICE_NAME,
    DEFAULT_GROUP_A_NAME,
    DEFAULT_GROUP_B_NAME,
    DEFAULT_UPDATE_INTERVAL,
    DOMAIN,
    LOGGER,
)


class AirodorWifiFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for Airodor Integration."""

    VERSION = 1

    @staticmethod
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> AirodorWifiOptionsFlowHandler:
        """Create the options flow for reconfiguration."""
        return AirodorWifiOptionsFlowHandler()

    async def async_step_user(
        self,
        user_input: dict | None = None,
    ) -> config_entries.ConfigFlowResult:
        """Handle a flow initialized by the user."""
        _errors = {}
        if user_input is not None:
            try:
                await self._test_credentials(
                    ip_address=user_input[CONF_IP_ADDRESS],
                )
            except UnicodeError as exception:
                LOGGER.warning(exception)
                _errors["base"] = "invalid_ip"
            except AirodorWifiApiClientCommunicationError as exception:
                LOGGER.error(exception)
                _errors["base"] = "connection"
            except AirodorWifiApiClientError as exception:
                LOGGER.exception(exception)
                _errors["base"] = "unknown"
            else:
                await self.async_set_unique_id(
                    # Use IP address as unique ID
                    unique_id=user_input[CONF_IP_ADDRESS]
                )
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=user_input.get(CONF_DEVICE_NAME, DEFAULT_DEVICE_NAME),
                    data=user_input,
                )

        integration = async_get_loaded_integration(self.hass, DOMAIN)
        assert integration.documentation is not None, (  # noqa: S101
            "Integration documentation URL is not set in manifest.json"
        )

        return self.async_show_form(
            step_id="user",
            description_placeholders={
                "documentation_url": integration.documentation,
            },
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_IP_ADDRESS,
                        default=(user_input or {}).get(CONF_IP_ADDRESS, vol.UNDEFINED),
                    ): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.TEXT,
                        ),
                    ),
                    vol.Optional(
                        CONF_UPDATE_INTERVAL,
                        default=(user_input or {}).get(
                            CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL
                        ),
                    ): selector.NumberSelector(
                        selector.NumberSelectorConfig(
                            min=5,
                            max=3600,
                            step=5,
                            unit_of_measurement="Minuten",
                            mode=selector.NumberSelectorMode.SLIDER,
                        ),
                    ),
                    vol.Optional(
                        CONF_DEVICE_NAME,
                        default=(user_input or {}).get(
                            CONF_DEVICE_NAME, DEFAULT_DEVICE_NAME
                        ),
                    ): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.TEXT,
                        ),
                    ),
                    vol.Optional(
                        CONF_AREA,
                        default=(user_input or {}).get(CONF_AREA, ""),
                    ): selector.AreaSelector(),
                    vol.Optional(
                        CONF_GROUP_A_NAME,
                        default=(user_input or {}).get(
                            CONF_GROUP_A_NAME, DEFAULT_GROUP_A_NAME
                        ),
                    ): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.TEXT,
                        ),
                    ),
                    vol.Optional(
                        CONF_GROUP_B_NAME,
                        default=(user_input or {}).get(
                            CONF_GROUP_B_NAME, DEFAULT_GROUP_B_NAME
                        ),
                    ): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.TEXT,
                        ),
                    ),
                },
            ),
            errors=_errors,
        )

    async def _test_credentials(self, ip_address: str) -> None:
        """Validate IP address and connectivity."""
        # Validate IP address format
        try:
            ipaddress.ip_address(ip_address)
        except ValueError as exception:
            msg = f"Invalid IP address format: {ip_address}"
            raise UnicodeError(msg) from exception

        # Test connectivity
        client = AirodorWifiApiClient(
            ip_address=ip_address,
            session=async_create_clientsession(self.hass),
        )
        await client.async_get_data()


class AirodorWifiOptionsFlowHandler(config_entries.OptionsFlow):
    """Options flow for Airodor Integration (allows reconfiguration)."""

    async def async_step_init(
        self,
        user_input: dict | None = None,
    ) -> config_entries.ConfigFlowResult:
        """Handle options flow."""
        if user_input is not None:
            # Merge updated options into entry data and trigger reload
            self.hass.config_entries.async_update_entry(
                self.config_entry,
                data={**self.config_entry.data, **user_input},
            )
            await self.hass.config_entries.async_reload(self.config_entry.entry_id)
            return self.async_create_entry(title="", data={})

        current = self.config_entry.data
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_UPDATE_INTERVAL,
                        default=current.get(
                            CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL
                        ),
                    ): selector.NumberSelector(
                        selector.NumberSelectorConfig(
                            min=5,
                            max=3600,
                            step=5,
                            unit_of_measurement="Minuten",
                            mode=selector.NumberSelectorMode.SLIDER,
                        ),
                    ),
                    vol.Optional(
                        CONF_DEVICE_NAME,
                        default=current.get(CONF_DEVICE_NAME, DEFAULT_DEVICE_NAME),
                    ): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.TEXT,
                        ),
                    ),
                    vol.Optional(
                        CONF_GROUP_A_NAME,
                        default=current.get(CONF_GROUP_A_NAME, DEFAULT_GROUP_A_NAME),
                    ): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.TEXT,
                        ),
                    ),
                    vol.Optional(
                        CONF_GROUP_B_NAME,
                        default=current.get(CONF_GROUP_B_NAME, DEFAULT_GROUP_B_NAME),
                    ): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.TEXT,
                        ),
                    ),
                },
            ),
        )
