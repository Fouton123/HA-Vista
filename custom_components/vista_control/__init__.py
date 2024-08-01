from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform, CONF_PORT
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN, CONNECTION
from .serial import SerialComm

ATTRIBUTION = "Vista"
DEFAULT_BRAND = "Vista Vista"

PLATFORMS = [Platform.ALARM_CONTROL_PANEL, Platform.SENSORS]


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Set up the Agent component."""
    hass.data.setdefault(DOMAIN, {})

    serial_port = config_entry.data[CONF_PORT]


    serial_client = SerialComm(serial_port, config_entry.entry_id)

    if not serial_client.exists():
        raise ConfigEntryNotReady

    hass.data[DOMAIN][config_entry.entry_id] = {CONNECTION: serial_client}

    device_registry = dr.async_get(hass)

    device_registry.async_get_or_create(
        config_entry_id=config_entry.entry_id,
        identifiers={(DOMAIN, serial_client.id)},
        manufacturer="Vista",
        name=f"Vista Vista",
        model="128bpt",
        sw_version=1.0,
    )

    hass.config_entries.async_setup_platforms(config_entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(
        config_entry, PLATFORMS
    )

    await hass.data[DOMAIN][config_entry.entry_id][CONNECTION].close()

    if unload_ok:
        hass.data[DOMAIN].pop(config_entry.entry_id)

    return unload_ok
