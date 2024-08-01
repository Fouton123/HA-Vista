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

    async def open_serial(self, device, baudrate, bytesize, parity, stopbits, xonxoff, rtscts, dsrdtr, **kwargs):
        logged_error = False
        try:
            self.reader, self.writer, _ = await serial_asyncio.open_serial_connection(url=self._port, baudrate=self._baudrate, bytesize=self._bytesize, parity=self._parity, stopbits=self._stopbits, xonxoff=self._xonxoff, rtscts=self._rtscts, dsrdtr=self._dsrdtr)
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

    async def serial_send(self, message):
        if self.writer is None:
            self.serial_open()
        else:
            self.writer.write(message)



    async def serial_read(self):
        """Read the data from the port."""
        logged_error = False
        while True:
            if self.reader is None:
                self.serial_open()
            else:
                while True:
                    try:
                        line = await self.reader.readline()
                    except SerialException as exc:
                        _LOGGER.exception(
                            "Error while reading serial device %s: %s", self._port, exc
                        )
                        await self._handle_error()
                        break
                    else:
                        line = line.decode("utf-8").strip()

                        try:
                            data = json.loads(line)
                        except ValueError:
                            pass
                        else:
                            if isinstance(data, dict):
                                self._attributes = data

                        Type = line[4:6]
                        Zone = line[6:9]
                        User = line[9:12]
                        Part = line[12:13]
                        MM = line[13:15]
                        HH = line[15:17]
                        DD = line[17:19]
                        mm = line[19:21]
                        YY = line[21:23]
            
                        #Armed/Disarmed
                        if Type == "07":
                            self._armed = "Armed"
                            self._armedIco = "mdi:lock"
                            self._user = "Armed by:" + str(int(User))
                            
                        if Type == "08":
                            self._armed = "Disarmed"
                            self._armedIco = "mdi:lock-open"
                            self._user = "Disarmed by:" + str(int(User))
                            
                        if Type == "07" or Type == "08":
                            self._tStampA = str(HH) + ":" + str(MM)
                            self._dStampA = str(mm) + "/" + str(DD) + "/" + str(YY) 
                            line = self._state

                        #Zone Status
                        if Type == "F5":
                            Zone = int(Zone)
                            self._zone = "Fault: " + self._sys_data["zones"][str(Zone)]
                            self._zoneIco = "mdi:alarm-light-outline"

                        if Type == "F6":
                            Zone = int(Zone)
                            self._zone = "Restore: " + self._sys_data["zones"][str(Zone)]
                            self._zoneIco = "mdi:alarm-light-off-outline"

                        if Type == "F5" or Type == "F6":
                            self._tStampF = str(HH) + ":" + str(MM)
                            self._dStampF = str(mm) + "/" + str(DD) + "/" + str(YY) 
                            line = self._state

                        if self._template is not None:
                            line = self._template.async_render_with_possible_json_value(
                                line
                            )

                        _LOGGER.debug("Received: %s", line)
                        self._state = line
                        self.async_write_ha_state()
