import voluptuous as vol
from homeassistant import config_entries
from .const import DOMAIN

DATA_SCHEMA = vol.Schema({
    vol.Required("application_id"): str,
    vol.Required("access_token"): str
})

class WOTConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow для WOT."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="WOT Reserves", data=user_input)

        return self.async_show_form(step_id="user", data_schema=DATA_SCHEMA)
