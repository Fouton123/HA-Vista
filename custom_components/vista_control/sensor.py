"""Support for reading data from a serial port."""
from __future__ import annotations
import json
import logging
from pathlib import Path
from datetime import timedelta

from homeassistant.components.sensor import SensorEntity, SensorDeviceClass
from homeassistant.const import CONF_VALUE_TEMPLATE, EVENT_HOMEASSISTANT_STOP
from homeassistant.core import callback
from homeassistant.util import dt

from .const import CONNECTION, DOMAIN

from .helpers import decode_message, device_info

SCAN_INTERVAL = timedelta(seconds=1)
SYSTEM_DATA = "data.json"

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass, config_entry, async_add_entities, discovery_info=None
):
    
    base_path = Path(__file__).parent
    path = f'{base_path}/{SYSTEM_DATA}'
    f = open (path, "r")
    sys_data = json.loads(f.read())
    
    """Set up the Serial sensor platform."""
    sensor = hass.data[DOMAIN][config_entry.entry_id][CONNECTION]
    serialSensor = SerialSensor(sensor)
    armDate = ArmSensor("Arm Date", serialSensor, "DATE", sensor.id)
    armTime = ArmSensor("Arm Time", serialSensor, "TIME", sensor.id)
    armStat = ArmSensor("Arm Status", serialSensor, "STAT", sensor.id)
    armUser = ArmSensor("Arm User", serialSensor, "USER", sensor.id)
    
    zoneDate = ZonesSensor("Zone Date", serialSensor, "DATE", sensor.id)
    zoneTime = ZonesSensor("Zone Time", serialSensor, "TIME", sensor.id)
    zoneStat = ZonesSensor("Zone Status", serialSensor, "STAT", sensor.id)
    zoneZone = ZonesSensor("Zone ID", serialSensor, "ZONE", sensor.id, sys_data)
    sensors = [serialSensor, armDate, armTime, armStat, armUser, zoneDate, zoneTime, zoneStat, zoneZone]
    
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
        self._attr_device_info =  device_info(device_id)
        self._zone_id= zone_id
        self._serialSensor = serialSensor
        self._state = None
        self._serial_loop_task = None


    async def async_added_to_hass(self):
        """Handle when an entity is about to be added to Home Assistant."""
        self._serial_loop_task = self.hass.loop.create_task(
            self.sensorUpdate()
        )
        
    async def sensorUpdate(self, **kwargs):
        msg = decode_message(self._serialSensor._state)
        #Zone Status
        if str(msg[0]) == "F5" and str(msg[1]) == self._zone_id:
            self._state = "Fault"
            self._icon = "mdi:alarm-light-outline"

        if str(msg[0]) == "F6" and str(msg[1]) == self._zone_id:
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
        await self.sensorUpdate()

class ZonesSensor(SensorEntity):
    _attr_has_entity_name = True

    def __init__(self, name, serialSensor, data, device_id, zonelist=None):
        self._attr_name = name
        """Initialize the Reddit sensor."""
        self._icon = "mdi:lock"
        unique_id =  f'vista_{name}'
        self._attr_unique_id = unique_id
        self._zonelist = zonelist
        self._attr_device_info =  device_info(device_id)
        self._serialSensor = serialSensor
        self._state = None
        self.data = data
        self.set_deice_class()
        self._serial_loop_task = None


    async def async_added_to_hass(self):
        """Handle when an entity is about to be added to Home Assistant."""
        self._serial_loop_task = self.hass.loop.create_task(
            self.sensorUpdate()
        )
        
    async def sensorUpdate(self, **kwargs):
        msg = decode_message(self._serialSensor._state)
        #Zone Status
        if str(msg[0]) == "F5" or str(msg[0]) == "F6":
            if self.data == "DATE":
                self._state = dt.utcnow().date()
                self._icon = "mdi:calendar-month-outline"
            if self.data == "TIME":
                self._state = dt.utcnow()
                self._icon = "mdi:clock-time-four-outline"
            if self.data == "ZONE":
                self._state = f'{msg[1]}: {self._zonelist["zones"][msg[1]]}'
                self._icon = "mdi:pound-box-outline"

        if str(msg[0]) == "F5" and self.data == "STAT":
            self._state = "Fault"
            self._icon = "mdi:alarm-light-outline"

        if str(msg[0]) == "F6" and self.data == "STAT":
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

    def set_deice_class(self):
        if self.data == "DATE":
            self._attr_device_class = SensorDeviceClass.DATE
        elif self.data == "TIME":
            self._attr_device_class = SensorDeviceClass.TIMESTAMP
        else:
            self._attr_device_class = None

    async def async_update(self):
        """Retrieve latest state."""
        await self.sensorUpdate()

class ArmSensor(SensorEntity):
    _attr_has_entity_name = True

    def __init__(self, name, serialSensor, data, device_id):

        self._attr_name = name
        self._icon = "mdi:lock"
        unique_id =  f'vista_{name}'
        self._attr_unique_id = unique_id
        self._attr_device_info =  device_info(device_id)
        self._serialSensor = serialSensor
        self._state = None
        self.data = data
        self.set_deice_class()
        self._serial_loop_task = None


    async def async_added_to_hass(self):
        """Handle when an entity is about to be added to Home Assistant."""
        self._serial_loop_task = self.hass.loop.create_task(
            self.sensorUpdate()
        )
        
    async def sensorUpdate(self, **kwargs):
        msg = decode_message(self._serialSensor._state)
        #Zone Status
        if str(msg[0]) == "07" or str(msg[0]) == "08":
            if self.data == "DATE":
                self._state = dt.utcnow().date()
                self._icon = "mdi:calendar-month-outline"
            if self.data == "TIME":
                self._state = dt.utcnow()
                self._icon = "mdi:clock-time-four-outline"
            if self.data == "USER":
                self._state = msg[2]
                self._icon = "mdi:account"

        if str(msg[0]) == "07" and self.data == "STAT":
            self._state = "Armed"
            self._icon = "mdi:lock"

        if str(msg[0]) == "08" and self.data == "STAT":
            self._state = "Disarmed"
            self._icon = "mdi:lock-open"

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

    def set_deice_class(self):
        if self.data == "DATE":
            self._attr_device_class = SensorDeviceClass.DATE
        elif self.data == "TIME":
            self._attr_device_class = SensorDeviceClass.TIMESTAMP
        else:
            self._attr_device_class = None

    async def async_update(self):
        """Retrieve latest state."""
        await self.sensorUpdate()

class SerialSensor(SensorEntity):
    _attr_has_entity_name = True
    _attr_name = "Vista-Serial"
    _attr_icon = "mdi:serial-port"

    def __init__(self, serial):
        """Initialize the Reddit sensor."""
        self._icon = "mdi:serial-port"
        self._attr_unique_id = 'serial_sensor'
        self._attr_device_info =  device_info(serial.id)
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