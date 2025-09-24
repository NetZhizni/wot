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

    main_sensor = WOTSensor(name, api_key, account_id, hass, async_add_entities)
    async_add_entities([main_sensor], True)

    # Встановлюємо періодичне оновлення
    async_track_time_interval(hass, main_sensor.async_update, SCAN_INTERVAL)


class WOTSensor(Entity):
    """Головний сенсор для кількості резервів."""

    def __init__(self, name, api_key, account_id, hass, async_add_entities):
        self._name = name
        self._api_key = api_key
        self._account_id = account_id
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

                # Динамічно створюємо дочірні сенсори
                new_sensors = []
                for r in reserves:
                    key = r["name"]
                    if key not in self.child_sensors:
                        sensor = WOTChildSensor(key, r, self._account_id)
                        self.child_sensors[key] = sensor
                        new_sensors.append(sensor)

                if new_sensors:
                    self.async_add_entities(new_sensors, True)

                # Оновлюємо значення вже існуючих дочірніх сенсорів
                for r in reserves:
                    key = r["name"]
                    self.child_sensors[key].update_state(r)

            else:
                self._state = 0
                self._attributes = {}

        except Exception as e:
            _LOGGER.error("Error fetching WOT reserves: %s", e)
            self._state = None
            self._attributes = {}


class WOTChildSensor(Entity):
    """Дочірній сенсор для окремого резерву."""

    def __init__(self, name, data, account_id):
        self._name = f"WOT Reserve {name}"
        self._data = data
        self._state = None
        self._account_id = account_id
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
        """Оновлення даних сенсора."""
        self._data = data
        # Тут можна змінити на будь-який ключ для основного стану
        self._state = data.get("level", 1)  # наприклад рівень резерву
