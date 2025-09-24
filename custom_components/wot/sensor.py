import logging
import aiohttp
from datetime import timedelta
import async_timeout

from homeassistant.helpers.entity import Entity
from homeassistant.helpers.event import async_track_time_interval

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(minutes=1)  # оновлення кожну хвилину

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up the WOT sensor asynchronously."""
    name = config.get("name", "WOT Reserves")
    api_key = config.get("api_key")
    account_id = config.get("account_id")

    if not api_key or not account_id:
        _LOGGER.error("API key and account ID must be provided in configuration.yaml")
        return

    sensor = WOTSensor(name, api_key, account_id, hass)
    async_add_entities([sensor], True)

    # Встановлюємо періодичне оновлення
    async_track_time_interval(hass, sensor.async_update, SCAN_INTERVAL)


class WOTSensor(Entity):
    def __init__(self, name, api_key, account_id, hass):
        self._name = name
        self._api_key = api_key
        self._account_id = account_id
        self._state = None
        self._attributes = {}
        self.hass = hass

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state

    @property
    def extra_state_attributes(self):
        return self._attributes

    async def async_update(self, now=None):
        """Asynchronously fetch data from World of Tanks API."""
        url = (
            f"https://api.worldoftanks.eu/wot/account/reserves/"
            f"?application_id={self._api_key}&account_id={self._account_id}"
        )

        try:
            async with aiohttp.ClientSession() as session:
                with async_timeout.timeout(10):
                    async with session.get(url) as response:
                        data = await response.json()

            if "data" in data and str(self._account_id) in data["data"]:
                reserves = data["data"][str(self._account_id)]
                self._state = len(reserves)
                self._attributes = {r["name"]: r for r in reserves}
            else:
                self._state = 0
                self._attributes = {}

        except Exception as e:
            _LOGGER.error("Error fetching WOT reserves: %s", e)
            self._state = None
            self._attributes = {}
