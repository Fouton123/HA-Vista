"""Support for reading data from a serial port."""
from __future__ import annotations
import logging
from datetime import timedelta

from homeassistant.components.sensor import SensorEntity
from homeassistant.const import CONF_VALUE_TEMPLATE, EVENT_HOMEASSISTANT_STOP
from homeassistant.core import callback

from .const import CONNECTION, DOMAIN

from .helpers import decode_message, device_info

SCAN_INTERVAL = timedelta(seconds=1)

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass, config_entry, async_add_entities, discovery_info=None
):
    """Set up the Serial sensor platform."""

    sensor = hass.data[DOMAIN][config_entry.entry_id][CONNECTION]

    serialSensor = SerialSensor(sensor)
    zone1Sensor = VistaSensor("Zone 1 Status", 'mdi:alarm-light-outline' ,"1", serialSensor, sensor.id)
    #zoneSensor = ZoneSensor("Zone Status", "Zone", sensor)
    #userSensor = ZoneSensor("User ID", "User", sensor)
    #armedSensor = ZoneSensor("Alarm Status", "Armed", sensor)
    #timeASensor = ZoneSensor("Event Time", "TimeA", sensor)
    #timeFSensor = ZoneSensor("Event Time", "TimeF", sensor)
    #dateASensor = ZoneSensor("Event Date", "DateA", sensor)
    #dateFSensor = ZoneSensor("Event Date", "DateF", sensor)
        #userSensor = UserSensor("Security User")
    
    hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STOP, serialSensor.stop_serial_read)
    hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STOP, zone1Sensor.stop_serial_read)
    #hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STOP, armedSensor.stop_serial_read)
    #hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STOP, timeASensor.stop_serial_read)
    #hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STOP, timeFSensor.stop_serial_read)
    #hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STOP, dateASensor.stop_serial_read)
    #hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STOP, dateFSensor.stop_serial_read)

    async_add_entities([serialSensor, zone1Sensor], True)
    #async_add_entities([zoneSensor], True)
    #async_add_entities([userSensor], True)
    #async_add_entities([armedSensor], True)
    #async_add_entities([timeASensor], True)
    #async_add_entities([timeFSensor], True)
    #async_add_entities([dateASensor], True)
    #async_add_entities([dateFSensor], True)

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
        return "TEST"

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


class VistaSensor(SensorEntity):
    _attr_has_entity_name = True

    def __init__(self, name, icon, type, serialSensor, device_id):
        """Initialize the Reddit sensor."""
        self._icon = icon
        self._attributes = None

        unique_id =  f'vista_zone_{type}'
        self._attr_unique_id = unique_id
        self._attr_device_info =  device_info(device_id, name)
        self._type = type
        self._serialSensor = serialSensor
        self._state = None
        self._serial_loop_task = None
        self.retVal = None


    async def async_added_to_hass(self):
        """Handle when an entity is about to be added to Home Assistant."""
        self._serial_loop_task = self.hass.loop.create_task(
            self.sensorUpdate()
        )
        
    async def sensorUpdate(self, **kwargs):
        msg = decode_message(self._serialSensor._state)
        #if self._type == msg[0]:
        if msg is None:
            self._state = self._state
        else:
            self._state = msg[1]
        #else:


    @callback
    def stop_serial_read(self, event):
        """Close resources."""
        if self._serial_loop_task:
            self._serial_loop_task.cancel()

    @property
    def native_value(self):
        """Return the state of the sensor."""
        return "TEST"

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        return self._attributes

    @property
    def icon(self):
        """Return the icon to use in the frontend."""
        return self._icon
        

    async def async_update(self):
        """Retrieve latest state."""
        msg = decode_message(self._serialSensor._state)
        if msg is None:
            self._state = self._state
        else:
            self._state = msg[1]
        

class SerialSensor(SensorEntity):
    _attr_has_entity_name = True
    _attr_native_value = "STR"

    def __init__(self, serial):
        """Initialize the Reddit sensor."""
        self._icon = "mdi:serial-port"
        self._name = "Vista-Serial"
        self._attr_name = self._name
        self._attributes = None

        self._attr_unique_id = 'serial_sensor'
        self._attr_device_info =  device_info(serial.id, self._name)
        self._serialSensor = serial
        self._state = None
        self._serial_loop_task = None
        self.retVal = None


    async def async_added_to_hass(self):
        """Handle when an entity is about to be added to Home Assistant."""
        self._serial_loop_task = self.hass.loop.create_task(
            self.serial_read()
        )
        
    async def serial_read(self, **kwargs):
        while True:
            self._state = "TEST1"
            self._state = await self._serialSensor.serial_read()
            
    def update(self):
        """Retrieve latest state."""
        self._state = self._state = self._serialSensor.serial_read()

    async def async_update(self):
        """Retrieve latest state."""
        self._state = "TEST"
        
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
        return "mdi:serial-port"
