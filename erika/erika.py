import time
from enum import Enum

import serial

from erika.erica_encoder_decoder import DDR_ASCII
from erika.util import twos_complement_hex_string
from erika_fs.ansii_decoder import *

ERIKA_BAUDRATE = 1200

DEFAULT_DELAY = 0.0
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


class AbstractErika(EscapeSequenceDecoder):

    # verify that all "public" methods are part of this "interface" class
    def __new__(cls, *args, **kwargs):
        not_found_methods = set()

        # search through method resolution order
        method_resolution_order = cls.__mro__
        for base_class in method_resolution_order:
            for name, value in base_class.__dict__.items():
                if not name.startswith("_") and name not in AbstractErika.__dict__:
                    not_found_methods.add(name)
        if not_found_methods:
            raise TypeError("Can't instantiate abstract class {}. All public methods (not starting with underscore) "
                            "must be part of the AbstractErika base class: {}"
                            .format(cls.__name__, ', \n'.join(not_found_methods)))
        else:
            return super(AbstractErika, cls).__new__(cls)


    @enforcedmethod
    def alarm(self, duration):
        pass

    @enforcedmethod
    def read(self):
        pass

    @enforcedmethod
    def print_ascii(self, text):
        pass

    @enforcedmethod
    def move_up(self):
        pass

    @enforcedmethod
    def move_down(self):
        pass

    @enforcedmethod
    def move_left(self):
        pass

    @enforcedmethod
    def move_right(self):
        pass

    @enforcedmethod
    def move_down_microstep(self):
        pass

    @enforcedmethod
    def move_up_microstep(self):
        pass

    @enforcedmethod
    def move_right_microsteps(self, num_steps=1):
        pass

    @enforcedmethod
    def move_left_microsteps(self, num_steps=1):
        pass

    @enforcedmethod
    def crlf(self):
        pass

    @enforcedmethod
    def set_keyboard_echo(self, value):
        pass

    @enforcedmethod
    def demo(self):
        pass

    @enforcedmethod
    def print_pixel(self):
        pass

    # TODO discuss if we need this everywhere
    # @enforcedmethod
    def decode(self, string):
        pass

    @enforcedmethod
    def wait_for_user_if_simulated(self):
        pass



class Erika(AbstractErika):

    def __init__(self, com_port, rts_cts=True, *args, **kwargs):
        """Set comport to serial device that connects to Erika typewriter."""
        self.com_port = com_port
        self.connection = serial.Serial(com_port, ERIKA_BAUDRATE, rtscts=rts_cts)  # , timeout=0, parity=serial.PARITY_EVEN, rtscts=1)
        self.ddr_ascii = DDR_ASCII()
        self.use_rts_cts = rts_cts

    ## resource manager stuff

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.connection.close()

    ##########################

    def alarm(self, duration):
        """Sound alarm for given duration [s]"""
        assert duration <= 5.1, "duration must be less than or equal to 5.1 seconds"
        duration /= 0.02
        duration_hex = hex(round(duration))
        self._write_byte("AA")
        self._write_byte(duration_hex[1:])
        # self.connection.write(b"\xaa\xff")

    def read(self):
        """Read a character data from the Erika typewriter and try to decode it.
        Returns: ASCII encoded character
        """
        key_id = self.connection.read()
        return self.ddr_ascii.try_decode(key_id.hex().upper())

    def print_ascii(self, text, esc_sequences=False):
        """Print given string on the Erika typewriter."""
        if esc_sequences:
            self.decode(text)
        for c in text:
            key_id = self.ddr_ascii.encode(c)
            self._write_byte(key_id)

    def move_up(self):
        self._cursor_up()

    def move_down(self):
        self._cursor_down()

    def move_left(self):
        self._cursor_back()

    def move_right(self):
        self._cursor_forward()

    def move_down_microstep(self):
        self._write_byte("81")

    def move_up_microstep(self):
        self._write_byte("82")

    def move_right_microsteps(self, num_steps=1):
        while num_steps > 127:
            self._write_byte("A5")
            self._write_byte(twos_complement_hex_string(127))
            num_steps = num_steps - 127

        self._write_byte("A5")
        self._write_byte(twos_complement_hex_string(num_steps))

    def move_left_microsteps(self, num_steps=1):
        # two's complement numbers: negative value range is 1 bigger than positive (because 0 positive)
        while num_steps > 128:
            self._write_byte("A5")
            self._write_byte(twos_complement_hex_string(-128))
            num_steps = num_steps - 128

        self._write_byte("A5")
        self._write_byte(twos_complement_hex_string(-1 * num_steps))

    def print_pixel(self):
        """
        Print pixel and end up one microstep to the right of the initial position (in analogue to "normal" text printing)
        :return:
        """
        self.print_ascii(".")
        self.move_left_microsteps(MICROSTEPS_PER_CHARACTER_WIDTH - 1)

    def crlf(self):
        self._write_byte("77")

    def set_keyboard_echo(self, value):
        if value:
            self._write_byte("92")
        else:
            self._write_byte("91")

    def demo(self):
        self.crlf()
        # self._print_smiley()
        self._print_demo_rectangle()
        self._advance_paper()

    def _print_demo_rectangle(self):

        for i in range(0, 10):
            self.print_ascii(".")
            self.move_left_microsteps(MICROSTEPS_PER_CHARACTER_WIDTH - 1)

        self.move_left_microsteps(1)

        for i in range(0, 5):
            self.move_down_microstep()
            self.print_ascii(".")
            self.move_left_microsteps(MICROSTEPS_PER_CHARACTER_WIDTH)

        self.move_left_microsteps(1)

        for i in range(0, 10):
            self.print_ascii(".")
            self.move_left_microsteps(MICROSTEPS_PER_CHARACTER_WIDTH + 1)

        self.move_right_microsteps(1)

        for i in range(0, 5):
            self.move_up_microstep()
            self.print_ascii(".")
            self.move_left_microsteps(MICROSTEPS_PER_CHARACTER_WIDTH)

    def _print_precision_test(self):
        self.crlf()
        self.crlf()

        self.print_ascii(".")
        self.move_left_microsteps(MICROSTEPS_PER_CHARACTER_WIDTH)
        self.move_right_microsteps(256)
        self.print_ascii(".")
        self.move_left_microsteps(MICROSTEPS_PER_CHARACTER_WIDTH)

        self.move_down_microstep()
        self.move_down_microstep()

        self.move_left_microsteps(256)
        self.print_ascii(".")
        self.move_left_microsteps(MICROSTEPS_PER_CHARACTER_WIDTH)
        self.move_right_microsteps(256)
        self.print_ascii(".")

    def _advance_paper(self):
        """ move paper up / cursor down by 10 halfsteps"""
        self._scroll_up(5)  # self._cursor_down(5)

    def _print_smiley(self):
        """print a smiley"""
        self._write_byte('13')
        self._write_byte('1F')

    def _write_byte(self, data, delay=DEFAULT_DELAY):
        """prints base16 formated data"""
        self.connection.write(bytes.fromhex(data))

        if not self.use_rts_cts:
            time.sleep(delay)

    def _move_erika(self, direction: Direction, n=1):
        """
        Moves n full steps in the given direction.

        :param direction: direction to move: Direction
        :param n: number of full steps to move
        """
        self._write_byte(direction.value * (2 * n))

    def _cursor_up(self, n=1):
        self._move_erika(Direction.UP, n)

    def _cursor_down(self, n=1):
        self._move_erika(Direction.DOWN, n)

    def _cursor_forward(self, n=1):
        self._move_erika(Direction.RIGHT, n)

    def _cursor_back(self, n=1):
        self._move_erika(Direction.LEFT, n)

    def _cursor_next_line(self, n=1):
        self._cursor_down(n)
        self.print_ascii("\r")

    def _cursor_previous_line(self, n=1):
        self._cursor_up(n)
        self.print_ascii("\r")

    def _decode_character(self, char):
        key_id = self.ddr_ascii.encode(char)
        self._write_byte(key_id)

    def _cursor_horizontal_absolute(self, n=1):
        pass

    def _cursor_position(self, n=1, m=1):
        pass

    def _erase_in_display(self, n=0):
        pass

    def _erase_in_line(self, n=0):
        pass

    def _scroll_up(self, n=1):
        self._cursor_down(n)

    def _scroll_down(self, n=1):
        self._cursor_up(n)

    def _select_graphic_rendition(self, *n):
        pass

    def _aux_port_on(self):
        pass

    def _aux_port_off(self):
        pass

    def _device_status_report(self):
        pass

    def _save_cursor_position(self):
        pass

    def _restore_cursor_position(self):
        pass

    def wait_for_user_if_simulated(self):
        pass

