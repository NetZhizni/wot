import logging
import aiohttp
from datetime import timedelta
import async_timeout

from homeassistant.helpers.entity import Entity
from homeassistant.helpers.event import async_track_time_interval

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(minutes=1)


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up WOT sensors from a config entry."""
    application_id = entry.data["application_id"]
    access_token = entry.data["access_token"]

    main_sensor = WOTSensor("WOT Reserves", application_id, access_token, hass, async_add_entities)
    async_add_entities([main_sensor], True)

    async_track_time_interval(hass, main_sensor.async_update, SCAN_INTERVAL)


class WOTSensor(Entity):
    """Головний сенсор для кількості резервів."""

    def __init__(self, name, application_id, access_token, hass, async_add_entities):
        self._name = name
        self._application_id = application_id
        self._access_token = access_token
        self._state = None
        self._attributes = {}
        self.hass = hass
        self.async_add_entities = async_add_entities
        self.child_sensors = {}

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
        """Asynchronously fetch data from WOT API."""
        url = "https://api.worldoftanks.eu/wot/stronghold/clanreserves/"
        params = {"application_id": self._application_id, "access_token": self._access_token}

        try:
            async with aiohttp.ClientSession() as session:
                with async_timeout.timeout(10):
                    async with session.get(url, params=params) as response:
                        data = await response.json()

            if data.get("status") != "ok" or "data" not in data:
                _LOGGER.warning("Unexpected WOT API response")
                self._state = 0
                self._attributes = {}
                return

            reserves = data["data"]
            self._state = sum(len(r.get("in_stock", [])) for r in reserves)
            self._attributes = {r["name"]: r for r in reserves}

            # Динамічне створення дочірніх сенсорів
            new_sensors = []
            for r in reserves:
                reserve_name = r["name"]
                for idx, stock in enumerate(r.get("in_stock", []), start=1):
                    key = f"{reserve_name} #{idx}"
                    if key not in self.child_sensors:
                        sensor = WOTChildSensor(key, stock)
                        self.child_sensors[key] = sensor
                        new_sensors.append(sensor)
                    else:
                        self.child_sensors[key].update_state(stock)

            if new_sensors:
                self.async_add_entities(new_sensors, True)

        except Exception as e:
            _LOGGER.error("Error fetching WOT reserves: %s", e)
            self._state = None
            self._attributes = {}


class WOTChildSensor(Entity):
    """Дочірній сенсор для окремого екземпляру резерву."""

    def __init__(self, name, data):
        self._name = f"WOT {name}"
        self._data = data
        self._state = None
        self.update_state(data)

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state

    @property
    def extra_state_attributes(self):
        return self._data

    def update_state(self, data):
        self._data = data
        self._state = data.get("amount", 0)
