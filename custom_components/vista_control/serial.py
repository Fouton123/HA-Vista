import socket
import json
import asyncudp
from pathlib import Path

import logging

_LOGGER = logging.getLogger(__name__)


SYSTEM_DATA = "data.json"


class SerialComm:
    """Serial Interface"""

    line = None
    arm = None
    zones = None

    def __init__(self, ip, port, rport, id=None):
        """Initialize the Serial port."""

        _LOGGER.info("Security Initialize")
        self.ip = ip
        self.port = port
        self.rport = rport
        self.id = id
        self.udp = None
        self.ptup = None

    async def get_arm_stat(self):
        await self.serial_send("08as0064")
        msg1 = await self.serial_read()
        msg2 = await self.serial_read()
        msg3 = await self.serial_read()
        _LOGGER.error(f"{msg1} {msg2} {msg3}")
        partitions = msg2[4:12]
        self.arm = "Disarmed"
        for i in partitions:
            if i != "D":
                self.arm = "Armed"

    async def get_zone_stat(self):
        await self.serial_send("08as0064")
        msg1 = await self.serial_read()
        msg2 = await self.serial_read()
        msg3 = await self.serial_read()
        msg4 = await self.serial_read()
        msg5 = await self.serial_read()
        _LOGGER.error(f"{msg1} {msg2} {msg5}")
        self.zones = msg2[5:101]

    def exists(self):
        """Return if serial port exists"""
        return True

    def id(self):
        return id

    async def serial_send(self, message):
        _LOGGER.info("Security Send: %s", message)
        if self.ptup is None:
            await self.serial_open()
        self._interupt = True
        self.udp.sendto(message.encode("utf-8"), self.ptup)
        self._interupt = False

    async def serial_read(self):
        """Read the data from the port."""

        if self.udp is None:
            await self.serial_open()

        try:
            _LOGGER.info("Security Wait")
            line = await self.udp.recvfrom()
            self.line = line[0].decode("utf-8")
            
        except Exception as e:
            _LOGGER.error("Failed %s", e)
        return self.line

    async def serial_open(self):
        logged_error = False

        _LOGGER.info(
            "Security Open: Recv %s",
            (socket.gethostbyname(socket.getfqdn()), int(self.rport)),
        )
        try:
            # self.udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.udp = await asyncudp.create_socket(
                local_addr=("0.0.0.0", int(self.rport))
            )
            self.ptup = (self.ip, int(self.port))
        except Exception as e:
            _LOGGER.error("Failed %s", e)
        else:
            _LOGGER.info("Serial device %s connected")
