from homeassistant.core import HomeAssistant

DOMAIN = "wot_reserves"

async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the WOT Reserves integration."""
    return True
