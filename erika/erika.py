import time

import serial

from erika.erica_encoder_decoder import DDR_ASCII

DEFAULT_DELAY = 0.3
LINE_BREAK_DELAY = 2.0


class Erika:
    conversion_table_path = "erika/charTranslation.json"

    def __init__(self, com_port, *args, **kwargs):
        """Set comport to serial device that connects to Erika typewriter."""
        self.com_port = com_port
        self.connection = serial.Serial(com_port, 1200)  # , timeout=0, parity=serial.PARITY_EVEN, rtscts=1)
        self.ddr_ascii = DDR_ASCII()

    ## resource manager stuff

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.connection.close()

    ##########################

    def alarm(self, duration):
        """Sound alarm for as long as possible"""
        self._print_raw("AA")
        self._print_raw("FF")
        # self.connection.write(b"\xaa\xff")

    # TODO: use duration parameter instead of fixed value
    def read(self):
        """Read a character data from the Erika typewriter and try to decode it.
        Returns: ASCII encoded character
        """
        key_id = self.connection.read()
        print(key_id.hex().upper())
        return self.ddr_ascii.try_decode(key_id.hex().upper())

    def print_ascii(self, text):
        """Print given string on the Erika typewriter."""
        for c in text:
            key_id = self.ddr_ascii.encode(c)
            self._write_byte_delay(key_id)

    def move_up(self):
        self._print_raw("76")
        time.sleep(DEFAULT_DELAY)
        self._print_raw("76")
        time.sleep(DEFAULT_DELAY)

    def move_down(self):
        self._print_raw("75")
        time.sleep(DEFAULT_DELAY)
        self._print_raw("75")
        time.sleep(DEFAULT_DELAY)

    def move_left(self):
        self._print_raw("74")
        time.sleep(DEFAULT_DELAY)
        self._print_raw("74")
        time.sleep(DEFAULT_DELAY)

    def move_right(self):
        self._print_raw("73")
        time.sleep(DEFAULT_DELAY)
        self._print_raw("73")
        time.sleep(DEFAULT_DELAY)

    def crlf(self):
        self._print_raw("77")
        time.sleep(LINE_BREAK_DELAY)
        
    def set_keyboard_echo(self, value):
        if value:
            self._print_raw("92")
        else:
            self._print_raw("91")

    def demo(self):
        self._advance_paper()
        self._print_smiley()
        self._advance_paper()

    def _advance_paper(self):
        """ move paper up / cursor down by 10 halfsteps"""
        for i in range(0, 10):
            self.connection.write(b'\x75')  # TODO use self.move_down() instead?
            time.sleep(DEFAULT_DELAY)

    def _print_smiley(self):
        """print a smiley"""
        self._write_byte_delay('13')
        self._write_byte_delay('1F')

    def _write_byte_delay(self, data, delay=DEFAULT_DELAY):
        """print base16 encoded data with delay"""
        self._print_raw(data)
        time.sleep(delay)

    def _print_raw(self, data):
        """prints base16 formated data"""
        self.connection.write(bytes.fromhex(data))
