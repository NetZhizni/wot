import logging
import requests
from homeassistant.helpers.entity import Entity

_LOGGER = logging.getLogger(__name__)

def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the WOT sensor."""
    name = config.get("name", "WOT Reserves")
    api_key = config.get("api_key")
    account_id = config.get("account_id")

    if not api_key or not account_id:
        _LOGGER.error("API key and account ID must be provided in configuration.yaml")
        return

    add_entities([WOTSensor(name, api_key, account_id)], True)


class WOTSensor(Entity):
    def __init__(self, name, api_key, account_id):
        self._name = name
        self._api_key = api_key
        self._account_id = account_id
        self._state = None
        self._attributes = {}

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state

    @property
    def extra_state_attributes(self):
        return self._attributes

    def update(self):
        """Fetch data from World of Tanks API."""
        try:
            url = (
                f"https://api.worldoftanks.eu/wot/account/reserves/"
                f"?application_id={self._api_key}&account_id={self._account_id}"
            )

            response = requests.get(url, timeout=10)
            data = response.json()

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
