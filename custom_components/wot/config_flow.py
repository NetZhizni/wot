import logging
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

DATA_SCHEMA = vol.Schema({
    vol.Required("application_id"): str,
    vol.Required("access_token"): str
})

class WOTConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for WOT integration."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            # Можна додати перевірку токену через API
            return self.async_create_entry(title="WOT Reserves", data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=DATA_SCHEMA
        )
