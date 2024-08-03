from serial import SerialException
import serial_asyncio
import json
from pathlib import Path

import logging
_LOGGER = logging.getLogger(__name__)

DEFAULT_BAUDRATE = 9600
DEFAULT_BYTESIZE = serial_asyncio.serial.EIGHTBITS
DEFAULT_PARITY = serial_asyncio.serial.PARITY_NONE
DEFAULT_STOPBITS = serial_asyncio.serial.STOPBITS_ONE
DEFAULT_XONXOFF = False
DEFAULT_RTSCTS = False
DEFAULT_DSRDTR = False

SYSTEM_DATA = "data.json"

class SerialComm():
    """Serial Interface"""
    line = None

    def __init__(self, port, id=None):
        """Initialize the Serial port."""
        self._port = port
        self.id = id
        self._baudrate = DEFAULT_BAUDRATE
        self._bytesize = DEFAULT_BYTESIZE
        self._parity = DEFAULT_PARITY
        self._stopbits = DEFAULT_STOPBITS
        self._xonxoff = DEFAULT_XONXOFF
        self._rtscts = DEFAULT_RTSCTS
        self._dsrdtr = DEFAULT_DSRDTR
        self._interupt = False
        self._serial_loop_task = None
        self._attributes = None
        self.reader = None
        self.writer = None

        base_path = Path(__file__).parent
        path = f'{base_path}/{SYSTEM_DATA}'
        f = open (path, "r")
        self._sys_data = json.loads(f.read())

    def exists(self):
        """Return if serial port exists"""
        return True
    
    def id(self):
        return id

    async def serial_send(self, message):
        if self.writer is None:
            await self.serial_open()
        self._interupt = True
        self.writer.write(message.encode('utf-8'))
        self._interupt = False

        return line
    
    async def serial_read(self):
        """Read the data from the port."""
        if self.reader is None:
            await self.serial_open()

        while True:
            if self._interupt == False:
                try:
                    line = await self.reader.readline()
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
            self.reader, self.writer = await serial_asyncio.open_serial_connection(url=self._port, baudrate=self._baudrate, bytesize=self._bytesize, parity=self._parity, stopbits=self._stopbits, xonxoff=self._xonxoff, rtscts=self._rtscts, dsrdtr=self._dsrdtr)
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
