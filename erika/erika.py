import time
from enum import Enum
import serial

from erika.util import twos_complement_hex_string, reverse_string, number2hex
import erika.ddrscii_codec
LINE_BREAK_DELAY = 0.0

# confirmed experimentally
MICROSTEPS_PER_CHARACTER_WIDTH = 10

# confirmed experimentally
MICROSTEPS_PER_CHARACTER_HEIGHT = 20


# command characters should be mapped to enum constants like directions in this case
class Direction(Enum):
    RIGHT = "73"
    LEFT = "74"
    UP = "76"
    DOWN = "75"


special_chars = ["€", "@"]


class Margin(Enum):
    LEFT = "7E"
    RIGHT = "7F"
    RESET = "80"
    DISABLE = "8F"
    ENABLE = "90"


class LineSpacing(Enum):
    ONE = "84"
    ONEHALF = "85"
    DOUBLE = "86"


class CharacterSpacing(Enum):
    TEN = "87"
    TWELVE = "88"
    FIFTEEN = "89"


class Tabulator(Enum):
    SET = "7A"
    DELETE = "7B"
    DELETE_ALL = "7C"
    RESET_2_DEFAULT = "7D"  ## ?


class KeyboardCodes(Enum):
    DEFAULT = "97"
    RAW_MATRIX = "98"


class Autorepeat(Enum):
    ON = "9B"
    OFF = "9C"

class LineEndings(Enum):
    UNIX = "77"
    WINDOWS = "9F"

class Baudrate(Enum):
    BD_1200 = "10"
    BD_2400 = "08"
    BD_4800 = "04"
    BD_9600 = "02"
    BD_19200 = "01"

    baudrates = {
        BD_1200: 1200
        , BD_2400: 2400
        , BD_4800: 4800
        , BD_9600: 9600
        , BD_19200: 19200
    }

    @property
    def baud(self):
        return self.baudrates.value[self.value]


class Erika:
    DEFAULT_BAUDRATE = 1200
    DEFAULT_DELAY = 0.0

    def __init__(self, com_port, rts_cts=True, baudrate=None  *args, **kwargs):
        """Set comport to serial device that connects to Erika typewriter."""
        self.connection = serial.Serial()
        self.connection.port = com_port
        if baudrate is None:
            baudrate = Erika.DEFAULT_BAUDRATE
        self.connection.baudrate = baudrate
        self.connection.rtscts = rts_cts

        self.rts_cts = rts_cts
        self.line_ending = LineEndings.UNIX

    ## resource manager stuff

    def open(self):
        self.connection.open()

    def close(self):
        self.connection.close()

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, *args):
        self.close()

    ##########################

    def _read_bytes(self, size=1) -> bytes:
        """Read a character data from the Erika typewriter and try to decode it.
        Returns: ASCII encoded character
        """
        return self.connection.read(size=size)

    def _write_bytes(self, data: bytes):
        return self.connection.write(data)

    def read_string(self, size=1) -> str:
        return self._read_bytes(size=size).decode("DDRSCII")

    def print_string(self, text: str):
        """Print given string on the Erika typewriter."""
        return self._write_bytes(text.encode("DDRSCII"))

