from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform, CONF_IP_ADDRESS, CONF_PORT, CONF_BROADCAST_PORT
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN, CONNECTION, MANUFACTURER, MODEL
from .serial import SerialComm

import logging
_LOGGER = logging.getLogger(__name__)

ATTRIBUTION = "Vista"
DEFAULT_BRAND = "Vista Vista"

PLATFORMS = [Platform.ALARM_CONTROL_PANEL, Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Set up the Agent component."""
    hass.data.setdefault(DOMAIN, {})

    ip = config_entry.data[CONF_IP_ADDRESS]
    port = config_entry.data[CONF_PORT]
    rport = config_entry.data[CONF_BROADCAST_PORT]


    _LOGGER.info("Init - Security Initialize") 
    serial_client = SerialComm(ip, port, rport, config_entry.entry_id)
    await serial_client.load_json()
    if not serial_client.exists():
        raise ConfigEntryNotReady

    hass.data[DOMAIN][config_entry.entry_id] = {CONNECTION: serial_client}

    device_registry = dr.async_get(hass)

    device_registry.async_get_or_create(
        config_entry_id=config_entry.entry_id,
        identifiers = {(DOMAIN, serial_client.id)},
        manufacturer = MANUFACTURER,
        model = MODEL,
        name = "Security System",
        sw_version=1.0,
    )

    
    await hass.config_entries.async_forward_entry_setups(config_entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_forward_entry_unload(
        config_entry, PLATFORMS
    )

    await hass.data[DOMAIN][config_entry.entry_id][CONNECTION].close()

    if unload_ok:
        hass.data[DOMAIN].pop(config_entry.entry_id)

    return unload_ok
