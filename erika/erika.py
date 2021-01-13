from typing import Optional

import serial
import time
import erika.ddrscii_codec
from erika.char_map import Direction, LINE_FEED


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
            # self._move_down_hs()
            # self._move_down_hs()

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

