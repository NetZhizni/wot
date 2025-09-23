from homeassistant.core import HomeAssistant

DOMAIN = "wot"

async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the WOT integration."""
    return True
