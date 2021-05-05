import struct
from typing import Optional

import serial
import time
import erika.ddrscii_codec
from erika.char_map import Direction, LINE_FEED, MicroStep
from math import floor


def signed_byte(value):
    return struct.pack("b", value)


class Erika:
    DEFAULT_BAUD_RATE = 1200

    def __init__(self, com_port, rts_cts=True, baud_rate=None, *args, **kwargs):
        """Set comport to serial device that connects to Erika typewriter."""
        self.connection = serial.Serial()
        self.connection.port = com_port
        if baud_rate is None:
            baud_rate = Erika.DEFAULT_BAUD_RATE
        self.connection.baudrate = baud_rate
        self.connection.rtscts = rts_cts

    # resource manager stuff #

    def open(self):
        self.connection.open()

    def close(self):
        self.connection.flush()
        time.sleep(5)
        self.connection.close()

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, *args):
        self.close()

    ##########################

    def _read_bytes(self, size: int = 1) -> bytes:
        return self.connection.read(size=size)

    def _write_bytes(self, data: bytes) -> Optional[int]:
        return self.connection.write(data)

    def read_string(self, size: int = 1) -> str:
        return self._read_bytes(size=size).decode("DDRSCII")

    def print_string(self, text: str) -> Optional[int]:
        """Print given string on the Erika typewriter."""
        return self._write_bytes(text.encode("DDRSCII"))

    def _move_left_hs(self):
        self._write_bytes(Direction.LEFT)

    def _move_right_hs(self):
        self._write_bytes(Direction.RIGHT)

    def _move_up_hs(self):
        self._write_bytes(Direction.UP)

    def _move_down_hs(self):
        self._write_bytes(Direction.DOWN)

    def move_left(self, chars=1):
        for _ in range(chars):
            self.print_string("\b")

    def move_right(self, chars=1):
        for _ in range(chars):
            self.print_string(" ")

    def move_up(self, chars=1):
        for _ in range(chars):
            self._move_up_hs()
            self._move_up_hs()

    def move_down(self, chars=1):
        for _ in range(chars):
            self._write_bytes(LINE_FEED)

    def move_down_microstep(self, num_steps=1):
        for _ in range(num_steps):
            self._write_bytes(MicroStep.DOWN)

    def move_up_microstep(self, num_steps=1):
        for _ in range(num_steps):
            self._write_bytes(MicroStep.UP)

    def move_right_microsteps(self, num_steps=1):
        assert 0 <= num_steps <= 127, "num_steps must be in [0, 127]"
        self._write_bytes(MicroStep.LEFT_RIGHT + signed_byte(num_steps))

    def move_left_microsteps(self, num_steps=1):
        # two's complement numbers: negative value range is 1 bigger than positive (because 0 positive)
        assert 0 <= num_steps <= 128, "num_steps must be in [0, 128]"
        self._write_bytes(MicroStep.LEFT_RIGHT + signed_byte(-num_steps))


class JustifiedErika(Erika):

    def print_stretched_line(self, text: str, target_line_width: float):
        words = text.split(" ")

        if len(words) < 2:
            self.print_string(text)
            return
        else:
            spaces = len(words) - 1
            total_space_width = target_line_width - len(text) + spaces
            space_width = total_space_width / spaces

            for word in words:
                self.print_string(word)
                self.move_right(chars=floor(space_width))
                micro_steps = round((space_width - floor(space_width)) * 12)
                self.move_right_microsteps(num_steps=micro_steps)
