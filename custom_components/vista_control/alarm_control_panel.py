"""Support for Agent DVR Alarm Control Panels."""
from homeassistant.components.alarm_control_panel import AlarmControlPanelEntity, CodeFormat, AlarmControlPanelEntityFeature

from homeassistant.const import (
    STATE_ALARM_ARMED_AWAY,
    STATE_ALARM_DISARMED,
)
from homeassistant.helpers.entity import DeviceInfo

from .const import CONNECTION, DOMAIN

import logging
_LOGGER = logging.getLogger(__name__)
ICON = "mdi:security"

CONF_AWAY_MODE_NAME = "away"

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
    _attr_supported_features = (AlarmControlPanelEntityFeature.ARM_AWAY)
    _attr_code_format = CodeFormat.NUMBER

    def __init__(self, serial):
        """Initialize the alarm control panel."""
        self.serial_client = serial
        self._attr_name = CONST_ALARM_CONTROL_PANEL_NAME
        self._attr_unique_id = f"vista_alarm_control_panel"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, serial.id)},
            manufacturer="Vista",
            model=CONST_ALARM_CONTROL_PANEL_NAME,
            sw_version=1.0,
        )

    async def async_update(self):
        """Update the state of the device."""
        self._attr_state = self._attr_state

        #await self.serial_client.update()
        #self._attr_available = self.serial_client.is_available
        #armed = self.serial_client.is_armed
        #if armed is None:
        #    self._attr_state = None
        #    return
        #if armed:
        #    self._attr_state = STATE_ALARM_ARMED_AWAY
        #else:
        #    self._attr_state = STATE_ALARM_DISARMED

    async def async_alarm_disarm(self, code=None):
        """Send disarm command."""
        #await self.serial_client.disarm()
        _LOGGER.error(f'{code} DISARM')
        await self.serial_client.serial_send('0Ead042568002D')
        self._attr_state = STATE_ALARM_DISARMED

    async def async_alarm_arm_away(self, code=None):
        """Send arm away command. Uses custom mode."""
        #await self.serial_client.arm()
        #await self.serial_client.set_active_profile(CONF_AWAY_MODE_NAME)
        _LOGGER.error(f'{code} ARM')
        self._attr_state = STATE_ALARM_ARMED_AWAY