"""Support for reading data from a serial port."""
from __future__ import annotations
import logging
from datetime import timedelta

from homeassistant.components.sensor import SensorEntity
from homeassistant.const import CONF_VALUE_TEMPLATE, EVENT_HOMEASSISTANT_STOP
from homeassistant.core import callback

from .const import CONNECTION, DOMAIN

SCAN_INTERVAL = timedelta(seconds=1)

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass, config_entry, async_add_entities, discovery_info=None
):
    """Set up the Serial sensor platform."""

    sensor = hass.data[DOMAIN][config_entry.entry_id][CONNECTION]

    serialSensor = SerialSensor(sensor)
    zoneSensor = ZoneSensor("Zone Status", "Zone", serialSensor)
    userSensor = ZoneSensor("User ID", "User", serialSensor)
    armedSensor = ZoneSensor("Alarm Status", "Armed", serialSensor)
    timeASensor = ZoneSensor("Event Time", "TimeA", serialSensor)
    timeFSensor = ZoneSensor("Event Time", "TimeF", serialSensor)
    dateASensor = ZoneSensor("Event Date", "DateA", serialSensor)
    dateFSensor = ZoneSensor("Event Date", "DateF", serialSensor)
        #userSensor = UserSensor("Security User")
    
    hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STOP, zoneSensor.stop_serial_read)
    hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STOP, userSensor.stop_serial_read)
    hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STOP, armedSensor.stop_serial_read)
    hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STOP, timeASensor.stop_serial_read)
    hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STOP, timeFSensor.stop_serial_read)
    hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STOP, dateASensor.stop_serial_read)
    hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STOP, dateFSensor.stop_serial_read)

    async_add_entities([serialSensor], True)
    async_add_entities([zoneSensor], True)
    async_add_entities([userSensor], True)
    async_add_entities([armedSensor], True)
    async_add_entities([timeASensor], True)
    async_add_entities([timeFSensor], True)
    async_add_entities([dateASensor], True)
    async_add_entities([dateFSensor], True)

class SerialSensor(SensorEntity):
    def __init__(
        self,
        serial_client,
        ):
        self.client = serial_client
    async def async_added_to_hass(self):
        """Handle when an entity is about to be added to Home Assistant."""
        self._serial_loop_task = self.hass.loop.create_task(
            self.client.serial_read()
        )

    async def _handle_error(self):
        """Handle error for serial connection."""
        self._state = None
        self._attributes = None
        self.async_write_ha_state()
        await asyncio.sleep(5)

    @callback
    def stop_serial_read(self, event):
        """Close resources."""
        if self._serial_loop_task:
            self._serial_loop_task.cancel()

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def should_poll(self):
        """No polling needed."""
        return False

    @property
    def extra_state_attributes(self):
        """Return the attributes of the entity (if any JSON present)."""
        return self._attributes

    @property
    def native_value(self):
        """Return the state of the sensor."""
        return self._state

class ZoneSensor(SensorEntity):
    """Representation of a Reddit sensor."""

    def __init__(self, name, sensor, serialSensor):
        """Initialize the Reddit sensor."""
        self._name = name
        self._sensor = sensor
        self._serialSensor = serialSensor.client
        self._state = None
        self._serial_loop_task = None
        self._attributes = None
        self.retVal = None

    async def async_added_to_hass(self):
        """Handle when an entity is about to be added to Home Assistant."""
        self._serial_loop_task = self.hass.loop.create_task(
            self.sensorUpdate()
        )
        
    async def sensorUpdate(self, **kwargs):
        self._serialSensor.serial_read()
        # while True:
        if self._sensor == "Zone":
            self.retVal = self._serialSensor.zone
        if self._sensor == "User":
            self.retVal = self._serialSensor.user
        if self._sensor == "Armed":
            self.retVal = self._serialSensor.armed
        if self._sensor == "TimeA":
            self.retVal = self._serialSensor.tStampA
        if self._sensor == "DateA":
            self.retVal = self._serialSensor.dStampA
        if self._sensor == "TimeF":
            self.retVal = self._serialSensor.tStampF
        if self._sensor == "DateF":
            self.retVal = self._serialSensor.dStampF

        self._state = self.retVal

    @callback
    def stop_serial_read(self, event):
        """Close resources."""
        if self._serial_loop_task:
            self._serial_loop_task.cancel()

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def native_value(self):
        """Return the state of the sensor."""
        return self.retVal

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        return self._attributes

    @property
    def icon(self):
        """Return the icon to use in the frontend."""
        if self._sensor == "Zone":
            ret = self._serialSensor.zoneIco
        if self._sensor == "User":
            ret = self._serialSensor.userIco
        if self._sensor == "Armed":
            ret = self._serialSensor.armedIco
        if self._sensor == "TimeA" or  self._sensor == "TimeF":
            ret = self._serialSensor.tStampIco
        if self._sensor == "DateA" or  self._sensor == "DateF":
            ret = self._serialSensor.dStampIco
        return ret
        

    async def async_update(self):
        """Retrieve latest state."""
        if self._sensor == "Zone":
            self.retVal = self._serialSensor.zone
        if self._sensor == "User":
            self.retVal = self._serialSensor.user
        if self._sensor == "Armed":
            self.retVal = self._serialSensor.armed
        if self._sensor == "TimeA":
            self.retVal = self._serialSensor.tStampA
        if self._sensor == "DateA":
            self.retVal = self._serialSensor.dStampA
        if self._sensor == "TimeF":
            self.retVal = self._serialSensor.tStampF
        if self._sensor == "DateF":
            self.retVal = self._serialSensor.dStampF

        self._state = self.retVal

