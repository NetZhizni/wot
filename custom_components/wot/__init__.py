from homeassistant.core import HomeAssistant

DOMAIN = "wot"

async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the integration (for YAML, якщо буде, але зараз можна залишити True)."""
    return True

async def async_setup_entry(hass, entry):
    """Set up WOT integration from a config entry."""
    # Зберігаємо дані конфігурації, щоб сенсори могли до них звертатись
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = entry.data
    return True
