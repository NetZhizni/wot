import logging
from datetime import timedelta
import aiohttp
import async_timeout

from homeassistant.helpers.entity import Entity
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)
SCAN_INTERVAL = timedelta(minutes=1)


async def async_setup_entry(hass, entry, async_add_entities):
    """Створюємо сенсори після додавання інтеграції через UI."""
    config = entry.data
    application_id = config["application_id"]
    access_token = config["access_token"]

    coordinator = WOTDataUpdateCoordinator(hass, application_id, access_token)
    await coordinator.async_refresh()

    # Головний сенсор
    main_sensor = WOTMainSensor(coordinator, "WOT Reserves")
    sensors = [main_sensor]

    # Дочірні сенсори для кожного резерву
    for reserve in coordinator.data:
        name = reserve["name"]
        for idx, stock in enumerate(reserve.get("in_stock", []), start=1):
            sensors.append(WOTChildSensor(coordinator, f"{name} #{idx}", stock))

    async_add_entities(sensors, True)


class WOTDataUpdateCoordinator(DataUpdateCoordinator):
    """Координатор для асинхронного отримання даних WOT."""

    def __init__(self, hass, application_id, access_token):
        self.application_id = application_id
        self.access_token = access_token
        super().__init__(
            hass,
            _LOGGER,
            name="WOT Reserves Coordinator",
            update_interval=SCAN_INTERVAL,
        )

    async def _async_update_data(self):
        url = "https://api.worldoftanks.eu/wot/stronghold/clanreserves/"
        params = {"application_id": self.application_id, "access_token": self.access_token}

        try:
            async with aiohttp.ClientSession() as session:
                with async_timeout.timeout(10):
                    async with session.get(url, params=params) as resp:
                        data = await resp.json()
            if data.get("status") != "ok" or "data" not in data:
                raise UpdateFailed("Unexpected WOT API response")
            return data["data"]

        except Exception as e:
            raise UpdateFailed(f"Error fetching WOT reserves: {e}")


class WOTMainSensor(Entity):
    """Головний сенсор: загальна кількість резервів."""

    def __init__(self, coordinator, name):
        self.coordinator = coordinator
        self._name = name
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

    async def async_update(self):
        await self.coordinator.async_request_refresh()
        data = self.coordinator.data
        self._state = sum(len(r.get("in_stock", [])) for r in data)
        self._attributes = {r["name"]: r for r in data}


class WOTChildSensor(Entity):
    """Дочірній сенсор для кожного резерву."""

    def __init__(self, coordinator, name, stock):
        self.coordinator = coordinator
        self._name = f"WOT {name}"
        self.stock_index = stock
        self._state = stock.get("amount", 0)
        self._attributes = stock

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state

    @property
    def extra_state_attributes(self):
        return self._attributes

    async def async_update(self):
        await self.coordinator.async_request_refresh()
        # Оновлюємо дані по конкретному резерву
        for reserve in self.coordinator.data:
            for stock in reserve.get("in_stock", []):
                if stock == self._attributes:
                    self._state = stock.get("amount", 0)
                    self._attributes = stock
