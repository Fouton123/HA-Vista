import sys
import glob
import serial

from homeassistant.helpers.entity import DeviceInfo

from .const import DOMAIN, MANUFACTURER, MODEL

def list_ports():
    """ Lists serial port names

        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of the serial ports available on the system
    """
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result

def calc_checksum(string):
    #8 bit modulo 256 checksum
    mod = sum(string.encode('ascii')) % 256
    #Find the compliment
    mod = 256 - mod;
    #make it a all caps 2 digit string
    mod = str(hex(mod)).upper()[2:]
    if len(mod) == 1:
        mod = f'0{mod}'

    return string + mod 

def decode_message(message):
    if message is None:
        return None
    else:
        Type = message[4:6]
        Zone = message[6:9]
        User = message[9:12]
        Part = message[12:13]
        MM = message[13:15]
        HH = message[15:17]
        DD = message[17:19]
        mm = message[19:21]
        YY = message[21:23]

        values = [Type, Zone, User, Part]
        return values 
    
def device_info(id, name):
    return DeviceInfo(
            identifiers = {(DOMAIN, id)},
            manufacturer = MANUFACTURER,
            model = MODEL,
            name = 'security'
        )