import voluptuous as vol
import secrets

from homeassistant import config_entries
from homeassistant.const import CONF_PORT
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .serial import SerialComm
from .helpers import list_ports
from .const import DOMAIN

DEFAULT_PORT = 8090


class AgentFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle an Agent config flow."""

    def __init__(self):
        """Initialize the Agent config flow."""
        self.device_config = {}

    async def async_step_user(self, user_input=None):
        """Handle an Agent config flow."""
        errors = {}

        if user_input is not None:
            serial_port = user_input[CONF_PORT]

            serial_client = SerialComm(serial_port)
            if serial_client.exists():
                # Only a single instance of the integration
                if self._async_current_entries():
                    return self.async_abort(reason="single_instance_allowed")

                id = secrets.token_hex(6)
                await self.async_set_unique_id(id)

                self._abort_if_unique_id_configured(
                    updates={
                        serial_port: user_input['serial'],
                    }
                )

                self.device_config = {
                    CONF_PORT: serial_port,
                }

                return await self._create_entry('Vista Control')
            
            errors["base"] = "port_not_found"

        data = {
            vol.Required(
                CONF_PORT,
            ): vol.In(list_ports())
        }

        return self.async_show_form(
            step_id="user",
            description_placeholders=self.device_config,
            data_schema=vol.Schema(data),
            errors=errors,
        )

    async def _create_entry(self, server_name):
        """Create entry for device."""
        return self.async_create_entry(title=server_name, data=self.device_config)
