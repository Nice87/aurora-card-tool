"""Config flow and options flow for Aurora Card Tool."""
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.config_entries import OptionsFlowWithReload
from homeassistant.core import callback

from .const import DOMAIN

class AuroraCardToolConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Aurora Card Tool."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial setup step."""
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        if user_input is not None:
            return self.async_create_entry(title="Aurora Card Tool", data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Optional("enable_file_watcher", default=True): bool,
                vol.Optional("enable_ma_helpers", default=True): bool,
                vol.Optional("enable_z2m_topology", default=True): bool,
            })
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return AuroraCardToolOptionsFlow(config_entry)


class AuroraCardToolOptionsFlow(OptionsFlowWithReload):
    """Handle options flow and automatically trigger integration reload on change."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage configuration options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        current_watcher = self.config_entry.options.get("enable_file_watcher", self.config_entry.data.get("enable_file_watcher", True))
        current_ma = self.config_entry.options.get("enable_ma_helpers", self.config_entry.data.get("enable_ma_helpers", True))
        current_z2m = self.config_entry.options.get("enable_z2m_topology", self.config_entry.data.get("enable_z2m_topology", True))

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Optional("enable_file_watcher", default=current_watcher): bool,
                vol.Optional("enable_ma_helpers", default=current_ma): bool,
                vol.Optional("enable_z2m_topology", default=current_z2m): bool,
            })
        )