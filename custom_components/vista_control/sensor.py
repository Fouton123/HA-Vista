"""Support for reading data from a serial port."""
from __future__ import annotations
import json
import logging
from pathlib import Path
from datetime import timedelta

from homeassistant.components.sensor import SensorEntity
from homeassistant.const import CONF_VALUE_TEMPLATE, EVENT_HOMEASSISTANT_STOP
from homeassistant.core import callback

from .const import CONNECTION, DOMAIN

from .helpers import decode_message, device_info

SCAN_INTERVAL = timedelta(seconds=1)
SYSTEM_DATA = "data.json"

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass, config_entry, async_add_entities, discovery_info=None
):
    """Set up the Serial sensor platform."""
    sensor = hass.data[DOMAIN][config_entry.entry_id][CONNECTION]
    serialSensor = SerialSensor(sensor)

    base_path = Path(__file__).parent
    path = f'{base_path}/{SYSTEM_DATA}'
    f = open (path, "r")
    sys_data = json.loads(f.read())
    sensors = []
    for i in sys_data["zones"].keys():
        tmp_sense = ZoneSensor(sys_data["zones"][i],i, serialSensor, sensor.id)
        sensors.append(tmp_sense)
        hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STOP, tmp_sense.stop_serial_read)

    async_add_entities(sensors, True)

class ZoneSensor(SensorEntity):
    _attr_has_entity_name = True

    def __init__(self, name, zone_id, serialSensor, device_id):
        self._attr_name = name
        """Initialize the Reddit sensor."""
        self._icon = "mdi:alarm-light-outline"
        unique_id =  f'vista_zone_{zone_id}'
        self._attr_unique_id = unique_id
        self._attr_device_info =  device_info(device_id, name)
        self._zone_id= zone_id
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

        #Zone Status
        if msg[0] == "F5" and msg[1] == self._zone_id:
            Zone = int(Zone)
            self._state = "Fault"
            self._icon = "mdi:alarm-light-outline"

        if msg[0] == "F6" and msg[1] == self._zone_id:
            Zone = int(Zone)
            self._state = "Restore"
            self._icon = "mdi:alarm-light-off-outline"

    @callback
    def stop_serial_read(self, event):
        """Close resources."""
        if self._serial_loop_task:
            self._serial_loop_task.cancel()

    @property
    def native_value(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def icon(self):
        """Return the icon to use in the frontend."""
        return self._icon

    async def async_update(self):
        """Retrieve latest state."""
        self.sensorUpdate()

class SerialSensor(SensorEntity):
    _attr_has_entity_name = True
    _attr_name = "Vista-Serial"
    _attr_icon = "mdi:serial-port"

    def __init__(self, serial):
        """Initialize the Reddit sensor."""
        self._icon = "mdi:serial-port"
        self._attr_unique_id = 'serial_sensor'
        self._attr_device_info =  device_info(serial.id, "Vista-Serial")
        self._serialSensor = serial
        self._state = None
        self._serial_loop_task = None


    async def async_added_to_hass(self):
        """Handle when an entity is about to be added to Home Assistant."""
        self._serial_loop_task = self.hass.loop.create_task(
            self.serial_read()
        )
        
    async def serial_read(self, **kwargs):
        while True:
            self._state = await self._serialSensor.serial_read()

    @callback
    def stop_serial_read(self, event):
        """Close resources."""
        if self._serial_loop_task:
            self._serial_loop_task.cancel()

    @property
    def native_value(self):
        """Return the state of the sensor."""
        return self._state