"""Support for Agent DVR Alarm Control Panels."""

from homeassistant.components.alarm_control_panel import (
    AlarmControlPanelEntity,
    CodeFormat,
    AlarmControlPanelEntityFeature,
    AlarmControlPanelState,
)


from .const import CONNECTION, DOMAIN
from .helpers import calc_checksum, device_info

from pathlib import Path
import aiofiles
import json
import logging

_LOGGER = logging.getLogger(__name__)
ICON = "mdi:security"

CONF_AWAY_MODE_NAME = "away"
SYSTEM_DATA = "data.json"
CONST_ALARM_CONTROL_PANEL_NAME = "Alarm Panel"


async def async_setup_entry(
    hass, config_entry, async_add_entities, discovery_info=None
):
    """Set up the Vista Alarm Control Panels."""
    async_add_entities(
        [vistaBaseStation(hass.data[DOMAIN][config_entry.entry_id][CONNECTION])]
    )


class vistaBaseStation(AlarmControlPanelEntity):
    """Representation of an Agent DVR Alarm Control Panel."""

    _attr_icon = ICON
    _attr_supported_features = AlarmControlPanelEntityFeature.ARM_AWAY
    _attr_code_format = CodeFormat.NUMBER

    def __init__(self, serial):
        """Initialize the alarm control panel."""
        self.serial_client = serial
        self._attr_name = CONST_ALARM_CONTROL_PANEL_NAME
        self._attr_unique_id = f"vista_alarm_control_panel"
        self._attr_device_info = device_info(serial.id)

    async def async_update(self):
        """Update the state of the device."""
        try:
            if self.serial_client.arm == "Armed":
                self._attr_alarm_state = AlarmControlPanelState.ARMED_AWAY
            else:
                self._attr_alarm_state = AlarmControlPanelState.DISARMED
        except Exception as e:
            _LOGGER.error("Failed %s", e)
        # await self.serial_client.update()
        # self._attr_available = self.serial_client.is_available
        # armed = self.serial_client.is_armed
        # if armed is None:
        #    self._attr_state = None
        #    return
        # if armed:
        #    self._attr_state = STATE_ALARM_ARMED_AWAY
        # else:
        #    self._attr_state = STATE_ALARM_DISARMED

    async def async_alarm_disarm(self, code=None):
        base_path = Path(__file__).parent
        path = f"{base_path}/{SYSTEM_DATA}"
        f = await aiofiles.open(path, mode="r")
        self.sys_data = json.loads(await f.read())
        await f.close()

        # """Send disarm command."""
        # await self.serial_client.disarm()
        if code != None:
            if len(code) != 4:
                self._attr_state = self._attr_state
                _LOGGER.warn(f"incorrect code length")
            else:
                try:
                    id = self.sys_data["codes"][str(code)]
                    message = f"0Ead{id}{code}00"
                    message = calc_checksum(message)
                    await self.serial_client.serial_send(message + "\r\n")
                    self._attr_alarm_state = AlarmControlPanelState.DISARMED
                except:
                    _LOGGER.warn(f"incorrect code")

    async def async_alarm_arm_away(self, code=None):
        base_path = Path(__file__).parent
        path = f"{base_path}/{SYSTEM_DATA}"
        f = await aiofiles.open(path, mode="r")
        self.sys_data = json.loads(await f.read())
        await f.close()

        # """Send arm away command. Uses custom mode."""
        # await self.serial_client.disarm()
        if code != None:
            if len(code) != 4:
                self._attr_state = self._attr_state
                _LOGGER.warn(f"incorrect code length")
            else:
                try:
                    id = self.sys_data["codes"][str(code)]
                    message = f"0Eaa{id}{code}00"
                    message = calc_checksum(message)
                    await self.serial_client.serial_send(message + "\r\n")
                    self._attr_alarm_state = AlarmControlPanelState.ARMED_AWAY
                except:
                    _LOGGER.warn(f"incorrect code")
