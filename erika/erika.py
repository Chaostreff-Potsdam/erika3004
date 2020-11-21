from typing import Optional

import serial
import erika.ddrscii_codec


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
        return self._write_bytes(text.encode("DDRSCII", "ignore"))
