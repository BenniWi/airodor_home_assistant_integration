"""Adds config flow for Airodor Integration."""

from __future__ import annotations

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
    CONF_HOST,
    CONF_PORT,
    CONF_UPDATE_INTERVAL,
    DEFAULT_DEVICE_NAME,
    DEFAULT_GROUP_A_NAME,
    DEFAULT_GROUP_B_NAME,
    DEFAULT_PORT,
    DEFAULT_UPDATE_INTERVAL,
    DOMAIN,
    LOGGER,
)


class AirodorWifiFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for Airodor Integration."""

    VERSION = 1

    @staticmethod
    def async_get_options_flow(
        _config_entry: config_entries.ConfigEntry,
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
            host = user_input[CONF_HOST].strip()
            port = int(user_input.get(CONF_PORT, DEFAULT_PORT))
            if not host:
                _errors["base"] = "invalid_host"
            else:
                try:
                    await self._test_credentials(host=host, port=port)
                except AirodorWifiApiClientCommunicationError as exception:
                    LOGGER.error(exception)
                    _errors["base"] = "connection"
                except AirodorWifiApiClientError as exception:
                    LOGGER.exception(exception)
                    _errors["base"] = "unknown"
                else:
                    await self.async_set_unique_id(f"{host}:{port}")
                    self._abort_if_unique_id_configured()
                    return self.async_create_entry(
                        title=user_input.get(CONF_DEVICE_NAME, DEFAULT_DEVICE_NAME),
                        data={**user_input, CONF_HOST: host, CONF_PORT: port},
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
                        CONF_HOST,
                        default=(user_input or {}).get(CONF_HOST, vol.UNDEFINED),
                    ): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.TEXT,
                        ),
                    ),
                    vol.Optional(
                        CONF_PORT,
                        default=(user_input or {}).get(CONF_PORT, DEFAULT_PORT),
                    ): selector.NumberSelector(
                        selector.NumberSelectorConfig(
                            min=1,
                            max=65535,
                            step=1,
                            mode=selector.NumberSelectorMode.BOX,
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

    async def _test_credentials(self, host: str, port: int) -> None:
        """Test connectivity to the device."""
        client = AirodorWifiApiClient(
            host=host,
            port=port,
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
        _errors = {}
        if user_input is not None:
            host = user_input[CONF_HOST].strip()
            port = int(user_input.get(CONF_PORT, DEFAULT_PORT))
            if not host:
                _errors["base"] = "invalid_host"
            else:
                try:
                    await self._test_credentials(host=host, port=port)
                except AirodorWifiApiClientCommunicationError as exception:
                    LOGGER.error(exception)
                    _errors["base"] = "connection"
                except AirodorWifiApiClientError as exception:
                    LOGGER.exception(exception)
                    _errors["base"] = "unknown"
                else:
                    # Merge updated options into entry data and trigger reload
                    updated = {
                        **self.config_entry.data,
                        **user_input,
                        CONF_HOST: host,
                        CONF_PORT: port,
                    }
                    self.hass.config_entries.async_update_entry(
                        self.config_entry,
                        data=updated,
                    )
                    await self.hass.config_entries.async_reload(
                        self.config_entry.entry_id
                    )
                    return self.async_create_entry(title="", data={})

        current = self.config_entry.data
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_HOST,
                        default=(user_input or current).get(CONF_HOST, vol.UNDEFINED),
                    ): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.TEXT,
                        ),
                    ),
                    vol.Optional(
                        CONF_PORT,
                        default=(user_input or current).get(CONF_PORT, DEFAULT_PORT),
                    ): selector.NumberSelector(
                        selector.NumberSelectorConfig(
                            min=1,
                            max=65535,
                            step=1,
                            mode=selector.NumberSelectorMode.BOX,
                        ),
                    ),
                    vol.Optional(
                        CONF_UPDATE_INTERVAL,
                        default=(user_input or current).get(
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
                        default=(user_input or current).get(
                            CONF_DEVICE_NAME, DEFAULT_DEVICE_NAME
                        ),
                    ): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.TEXT,
                        ),
                    ),
                    vol.Optional(
                        CONF_GROUP_A_NAME,
                        default=(user_input or current).get(
                            CONF_GROUP_A_NAME, DEFAULT_GROUP_A_NAME
                        ),
                    ): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.TEXT,
                        ),
                    ),
                    vol.Optional(
                        CONF_GROUP_B_NAME,
                        default=(user_input or current).get(
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

    async def _test_credentials(self, host: str, port: int) -> None:
        """Test connectivity to the device."""
        client = AirodorWifiApiClient(
            host=host,
            port=port,
            session=async_create_clientsession(self.hass),
        )
        await client.async_get_data()
