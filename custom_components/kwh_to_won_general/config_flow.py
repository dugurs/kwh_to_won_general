"""Config flow for Damda Weather integration."""
from __future__ import annotations
from tokenize import Number
from urllib.parse import quote_plus, unquote
from homeassistant.const import CONF_NAME, CONF_DEVICE_CLASS, DEVICE_CLASS_ENERGY, ATTR_UNIT_OF_MEASUREMENT, ENERGY_KILO_WATT_HOUR
import voluptuous as vol
from homeassistant.core import callback

from homeassistant import config_entries

from .const import DOMAIN, WELFARE_DC_OPTION, PRESSURE_OPTION, CHECKDAY_OPTION

# import logging
# _LOGGER = logging.getLogger(__name__)

OPTION_LIST = [
    ("checkday_config", "required", 1, vol.In(CHECKDAY_OPTION)),
    ("pressure_config", "required", "F1-low", vol.In(PRESSURE_OPTION)),
    ("contractKWh_config", "required", 1, vol.All(vol.Coerce(float), vol.Range(min=0))),
    ("welfare_dc_config", "required", 0, vol.In(WELFARE_DC_OPTION)),
    ("usekwh_entity", "required", "", str),
    ("lagging_entity", "optional", "", str),
    ("leading_entity", "optional", "", str),
    # ("minkwh_entity", "required", "", str),
    # ("medkwh_entity", "required", "", str),
    # ("maxkwh_entity", "required", "", str),
    ("prev_usekwh_entity", "optional", "", str),
    ("prev_lagging_entity", "optional", "", str),
    ("prev_leading_entity", "optional", "", str),
    # ("prev_minkwh_entity", "optional", "", str),
    # ("prev_medkwh_entity", "optional", "", str),
    # ("prev_maxkwh_entity", "optional", "", str),
    ("calibration_config", "required", 0, vol.All(vol.Coerce(float), vol.Range(min=0, max=2)))
]

class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Damda Weather."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            return self.async_create_entry(title=user_input['device_name'], data=user_input)

        data_schema = {vol.Required('device_name'): str}
        for name, required, default, validation in OPTION_LIST:
            if required == "required":
                key = (
                    vol.Required(name, default=default)
                )
            else:
                key = (
                    vol.Optional(name, default=default)
                )
            data_schema[key] = validation
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(data_schema),
            errors=errors
        )

    async def async_step_import(self, user_input=None):
        """Handle configuration by yaml file."""
        await self.async_set_unique_id(user_input['device_name'])
        for entry in self._async_current_entries():
            if entry.unique_id == self.unique_id:
                self.hass.config_entries.async_update_entry(entry, data=user_input)
                self._abort_if_unique_id_configured()
        return self.async_create_entry(title=user_input['device_name'], data=user_input)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Handle a option flow."""
        return OptionsFlowHandler(config_entry)


class OptionsFlowHandler(config_entries.OptionsFlow):
    """Handle a option flow for Damda Pad."""

    def __init__(self, config_entry: config_entries.ConfigEntry):
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Handle options flow."""
        errors = {}

        conf = self.config_entry
        if conf.source == config_entries.SOURCE_IMPORT:
            return self.async_show_form(step_id="init", data_schema=None)
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        options_schema = {}
        for name, required, default, validation in OPTION_LIST:
            to_default = conf.options.get(name, conf.data.get(name, default))
            if required == "required":
                key = (
                    vol.Required(name, default=to_default)
                )
            else:
                key = (
                    vol.Optional(name, default=to_default)
                )
            options_schema[key] = validation
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(options_schema),
            errors=errors
        )