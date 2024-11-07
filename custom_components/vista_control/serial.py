from serial import SerialException
import socket
import json
from pathlib import Path

import logging
_LOGGER = logging.getLogger(__name__)


SYSTEM_DATA = "data.json"

class SerialComm():
    """Serial Interface"""
    line = None
    arm = None
    zones = None

    def __init__(self, ip, port, rport, id=None):
        """Initialize the Serial port."""
        self.ip = ip
        self.port = port
        self.rport = rport
        self.id = id
        self.udp = None
        self.ptup = None

        base_path = Path(__file__).parent
        path = f'{base_path}/{SYSTEM_DATA}'
        f = open (path, "r")
        self._sys_data = json.loads(f.read())

        
    async def get_arm_stat(self):
        await self.serial_send('08as0064')
        msg1 = await self.serial_read()
        msg2 = await self.serial_read()
        msg3 = await self.serial_read()
        _LOGGER.error(f'{msg1} {msg2} {msg3}')
        partitions = msg2[4:12]
        self.arm = "Disarmed"
        for i in partitions:
            if i != "D":
                self.arm = "Armed"

    async def get_zone_stat(self):
        await self.serial_send('08as0064')
        msg1 = await self.serial_read()
        msg2 = await self.serial_read()
        msg3 = await self.serial_read()
        msg4 = await self.serial_read()
        msg5 = await self.serial_read()
        _LOGGER.error(f'{msg1} {msg2} {msg5}')
        self.zones = msg2[5:101]

               
    def exists(self):
        """Return if serial port exists"""
        return True
    
    def id(self):
        return id

    async def serial_send(self, message):
        if self.ptup is None:
            await self.serial_open()
        self._interupt = True
        self.udp.sendto(message.encode('utf-8'), self.ptup)
        self._interupt = False

    async def serial_read(self):
        """Read the data from the port."""
        if self.udp is None:
            await self.serial_open()

        while True:
            if self._interupt == False:
                try:
                    line = await self.udp.recv(1024)[0]
                except SerialException as exc:
                    _LOGGER.exception(
                        "Error while reading serial device %s: %s", self._port, exc
                    )
                    await self._handle_error()
                    break
                else:
                    self.line = line.decode("utf-8").strip()

                    return self.line

    async def serial_open(self):
        logged_error = False
        try:
            self.udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
            self.udp.bind(('0.0.0.0', int(self.rport)))
            self.ptup = (self.ip, int(self.port))
        except SerialException as exc:
                if not logged_error:
                    _LOGGER.exception(
                        "Unable to connect to the serial device %s: %s. Will retry",
                        self._port,
                        exc,
                    )
                    logged_error = True
                await self._handle_error()
        else:
            _LOGGER.info("Serial device %s connected", self._port)
