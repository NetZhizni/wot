from homeassistant.core import HomeAssistant
from .const import DOMAIN

async def async_setup(hass: HomeAssistant, config: dict):
    """Для YAML-налаштування (не використовується)."""
    return True

async def async_setup_entry(hass, entry):
    """Зберігаємо дані конфігурації для сенсорів."""
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = entry.data
    return True
