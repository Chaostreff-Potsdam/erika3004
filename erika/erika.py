import time
from enum import Enum

import serial

from erika.erica_encoder_decoder import DDR_ASCII
from erika.util import twos_complement_hex_string, reverse_string, number2hex
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
    RESET_2_DEFAULT = "7D"


class KeyboardCodes(Enum):
    DEFAULT = "97"
    RAW_MATRIX = "98"


class Autorepeat(Enum):
    ON = "9B"
    OFF = "9C"


class Baudrate(Enum):
    BD_1200 = "10"
    BD_2400 = "08"
    BD_4800 = "04"
    BD_9600 = "02"
    BD_19200 = "01"


class AbstractErika:
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

    @enforcedmethod
    def delete_pixel(self):
        pass

    @enforcedmethod
    def delete_ascii(self, reversed_text):
        pass

    def set_margin(self, margin_side):
        pass
    
    def set_spacing(self, line_spacing):
        pass

    def set_character_spacing(self, character_spacing):
        pass

    def reset(self):
        pass

    def set_tabs(self, tabulator):
        pass

    def set_keyboard_code(self, code):
        pass

    def enable_autorepeat(self, value):
        pass

    def set_baudrate(self, baudrate):
        pass


class Erika(AbstractErika):

    def __init__(self, com_port, rts_cts=True, *args, **kwargs):
        """Set comport to serial device that connects to Erika typewriter."""
        self.connection = serial.Serial()
        self.connection.port = com_port
        self.connection.baudrate = ERIKA_BAUDRATE
        self.connection.rtscts = rts_cts

        self.ddr_ascii = DDR_ASCII()
        self.use_rts_cts = rts_cts

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

    def alarm(self, duration):
        """Sound alarm for given duration [s]"""
        assert duration <= 5.1, "duration must be less than or equal to 5.1 seconds"
        duration /= 0.02
        duration_hex = number2hex(round(duration))
        self._write_byte("AA")
        self._write_byte(duration_hex)
        # self.connection.write(b"\xaa\xff")

    def read(self):
        """Read a character data from the Erika typewriter and try to decode it.
        Returns: ASCII encoded character
        """
        key_id = self.connection.read()
        return self.ddr_ascii.try_decode(key_id.hex().upper())
    
    def _overprint_byte(self, c):
        self._write_byte("A9")
        self._write_byte(c)
    
    def overprint_ascii(self, text):
        for c in text[-1]:
            key_id = self.ddr_ascii.encode(c)
            self._overprint_char(key_id)
        self.print_ascii(text[-1])    
        
    
    def _print_special_chars(self, c):
        if c == "€":
            self.overprint_ascii("C=")
        elif c == "@":
            self.overprint_ascii("Qa")

    def print_ascii(self, text, esc_sequences=False):
        """Print given string on the Erika typewriter."""
        if esc_sequences:
            self.decode(text)
        for c in text:
            if c in special_chars:
                self._print_special_chars(c)
            else:
                key_id = self.ddr_ascii.encode(c)
                self._write_byte(key_id)

    def _fast_print(self, text):
        """uses reverse printing mode to print even faster"""
        lines = text.split("\n")
        assert len(lines) >= 2, "need at least 2 lines to use fast_printing"
        for line_even, line_odd in zip(lines[::2], lines[1::2]):
            self.print_ascii(line_even.ljust(len(line_odd)))

            self.move_down()

            self._set_reverse_printing_mode(True)
            line_odd = reverse_string(line_odd).rjust(len(line_even))
            self.print_ascii(line_odd)
            self._set_reverse_printing_mode(False)

            self.move_down()

    def _set_reverse_printing_mode(self, value):
        if value:
            self._write_byte("8E")
        else:
            self._write_byte("8D")

    def _set_correction_mode(self, value):
        """Enable / Disable correction mode - i.e. for True, switch to correction tape, for False, switch to normal tape"""
        if value:
            self._write_byte("8C")
        else:
            self._write_byte("8B")

    def delete_ascii(self, reversed_text):
        """Delete given string on the Erika typewriter, going backwards."""

        # enable correction_mode and reverse printing
        self._set_correction_mode(True)
        self._set_reverse_printing_mode(True)

        # send text to be deleted
        self.print_ascii(reversed_text)

        # reset to normal operating mode
        self._set_reverse_printing_mode(False)
        self._set_correction_mode(False)

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

    def delete_pixel(self):
        """deletes pixel at current coursor, moves left afterwards"""
        self.delete_ascii(".")

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

    def set_margin(self, margin_side):
        self._write_byte(margin_side.value)

    def set_line_spacing(self, line_spacing):
        self._write_byte(line_spacing.value)

    def set_character_spacing(self, character_spacing):
        self._write_byte(character_spacing.value)

    def reset(self):
        self._write_byte("95")

    def set_tabs(self, tabulator):
        self._write_byte(tabulator.value)

    def set_keyboard_code(self, code):
        self._write_byte(code.value)

    def enable_autorepeat(self, value):
        if value:
            self._write_byte(Autorepeat.ON)
        else:
            self._write_byte(Autorepeat.OFF)

    def set_baudrate(self, baudrate):
        assert isinstance(baudrate, Baudrate), "Expected instance of type Baudrate"
        self._write_byte("A1")
        self._write_byte(baudrate.value)

    def set_velocity(self, velocity):
        assert 0 <= velocity <= 255, f"Velocity must be in range (0, 255) (inclusive), but was: {velocity}"
        self._write_byte("A3")
        self._write_byte(number2hex(velocity))

    def turn_typewheel(self, steps):
        assert 0 <= velocity <= 255, f"Steps must be in range (0, 255) (inclusive), but was: {velocity}"
        self._write_byte("A7")
        self._write_byte(number2hex(steps))

    def advance_ribbon(self, steps):
        assert 0 <= velocity <= 255, f"Steps must be in range (0, 255) (inclusive), but was: {velocity}"
        self._write_byte("A8")
        self._write_byte(number2hex(steps))
    
    def paper_feed(self):
        self._write_byte("83")