import re
from abc import ABC, abstractmethod
import inspect

ESC = "\x1B"  # = "\033" # = "\x1B" #
CSI = ESC + "["


def get_default_args(func):
    signature = inspect.signature(func)
    return {
        k: v.default
        for k, v in signature.parameters.items()
        if v.default is not inspect.Parameter.empty
    }


class InvalidEscapeSequenceError(ValueError):
    pass


# special decorator: enforce that subclasses implement the method
# See https://stackoverflow.com/a/25651022
def enforcedmethod(func):
    func.__enforcedmethod__ = True
    return func


class MetaclassForEnforcingMethods:

    # verify that enforced methods are implemented
    def __new__(cls, *args, **kwargs):
        method_names = set()
        not_found_enforced_methods = set()
        # search through method resolution order
        method_resolution_order = cls.__mro__
        for base_class in method_resolution_order:
            for name, value in base_class.__dict__.items():
                # method_names are collected in this dictionary while going up the inheritance hierarchy.
                # If the method is not in there when the method is marked <to be enforced in the current base_class,
                # it has not been implemented in a base class as expected.
                if getattr(value, "__enforcedmethod__", False) and name not in method_names:
                    not_found_enforced_methods.add(name)
                method_names.add(name)

        if not_found_enforced_methods:
            raise TypeError("Can't instantiate abstract class {} - must implement enforced methods {}"
                            .format(cls.__name__, ', \n'.join(not_found_enforced_methods)))
        else:
            return super(MetaclassForEnforcingMethods, cls).__new__(cls)


class EscapeSequenceDecoder(MetaclassForEnforcingMethods):
    """
    Based on https://en.wikipedia.org/wiki/ANSI_escape_code
    """

    def __init__(self):
        self.csi_codes = {
            "A": self._cursor_up
            , "B": self._cursor_down
            , "C": self._cursor_forward
            , "D": self._cursor_back
            , "E": self._cursor_next_line
            , "F": self._cursor_previous_line
            , "G": self._cursor_horizontal_absolute
            , "H": self._cursor_position
            , "J": self._erase_in_display
            , "K": self._erase_in_line
            , "S": self._scroll_up
            , "T": self._scroll_down
            , "f": self._cursor_position  # Horizontal Vertical Position: same as Cursor Position
            , "m": self._select_graphic_rendition
            , "i": self._decode_aux_port
            , "n": self._device_status_report
            , "s": self._save_cursor_position
            , "u": self._restore_cursor_position
        }

    def _decode_aux_port(self, n):
        if n == 5:
            self._aux_port_on()
        elif n == 4:
            self._aux_port_off()
        else:
            raise InvalidEscapeSequenceError("n must be either 5 (on) or 4 (off), but was {}".format(n))

    def _find_sequences(self, string):
        # this regex matches on ANSI escape sequences
        esc_seq_regex = "\x1B\\[((?:[0-9]?;?)*[\x40-\x7E])"  # "\x1B\\[([0-9]?;?)*[\x40-\x7E]"

        # make sure there are no unsupported escape sequences
        check = re.sub(esc_seq_regex, "", string)
        assert ESC not in check, "unsupported escape sequence found"

        # find all escape sequences
        escape_sequences = re.findall(esc_seq_regex, string)
        # replace them with just the ESC character
        string = re.sub(esc_seq_regex, ESC, string)

        return escape_sequences, string

    def _decode_escape_sequence(self, seq):
        command = seq[-1]
        params = seq[:-1].split(";")
        func = self.csi_codes[command]
        if command == "m":
            pass
        else:
            defaults = get_default_args(func)
            params = [default if p == "" else int(p) for default, p in zip(defaults.values(), params)]

        return self.csi_codes[command](*params)

    def decode(self, string):
        escape_sequences, string = self._find_sequences(string)

        for c in string:
            if c == ESC:
                self._decode_escape_sequence(escape_sequences.pop(0))
            else:
                self._decode_character(c)

    @abstractmethod
    def _decode_character(self, char):
        pass

    @abstractmethod
    def _cursor_up(self, n=1):
        """Moves the cursor n (default 1) cells up.
                If the cursor is already at the edge of the screen, this has no effect."""
        pass

    @abstractmethod
    def _cursor_down(self, n=1):
        """Moves the cursor n (default 1) cells down.
                If the cursor is already at the edge of the screen, this has no effect."""
        pass

    @abstractmethod
    def _cursor_forward(self, n=1):
        """Moves the cursor n (default 1) cells forward.
                If the cursor is already at the edge of the screen, this has no effect."""
        pass

    @abstractmethod
    def _cursor_back(self, n=1):
        """Moves the cursor n (default 1) cells back.
                If the cursor is already at the edge of the screen, this has no effect."""
        pass

    @abstractmethod
    def _cursor_next_line(self, n=1):
        """Moves cursor to beginning of the line n (default 1) lines down."""
        pass

    @abstractmethod
    def _cursor_previous_line(self, n=1):
        """Moves the cursor to column n (default 1)."""
        pass

    @abstractmethod
    def _cursor_horizontal_absolute(self, n=1):
        """Moves cursor to beginning of the line n (default 1) lines up."""
        pass

    @abstractmethod
    def _cursor_position(self, n=1, m=1):
        """
        Moves the cursor to row n, column m.
                The values are 1-based, and default to 1 (top left corner) if omitted.
                A sequence such as CSI ;5H is a synonym for CSI 1;5H
                as well as CSI 17;H is the same as CSI 17H and CSI 17;1H
        """
        pass

    @abstractmethod
    def _erase_in_display(self, n=0):
        """
        Clears part of the screen.

        :param n: If n is 0 (or missing), clear from cursor to end of screen.
        If n is 1, clear from cursor to beginning of the screen.
        If n is 2, clear entire screen (and moves cursor to upper left on DOS ANSI.SYS).
        If n is 3, clear entire screen and delete all lines saved in the scrollback buffer
        (this feature was added for xterm and is supported by other terminal applications).

        :return: None
        """
        pass

    @abstractmethod
    def _erase_in_line(self, n=0):
        """
        Erases part of the line.
        :param n: If n is 0 (or missing), clear from cursor to the end of the line.
            If n is 1, clear from cursor to beginning of the line.
            If n is 2, clear entire line. Cursor position does not change.
        :return: None
        """
        pass

    @abstractmethod
    def _scroll_up(self, n=1):
        """
        Scroll whole page up by n (default 1) lines.
        New lines are added at the bottom. (not ANSI.SYS)
        """
        pass

    @abstractmethod
    def _scroll_down(self, n=1):
        """
        Scroll whole page down by n (default 1) lines.
        New lines are added at the top. (not ANSI.SYS)
        """
        pass

    @abstractmethod
    def _select_graphic_rendition(self, *n):
        """
        Sets the appearance of the following characters, see SGR parameters below.
        """
        pass

    @abstractmethod
    def _aux_port_on(self):
        """
        Enable aux serial port usually for local serial printer.
        """
        pass

    @abstractmethod
    def _aux_port_off(self):
        """
        Disable aux serial port usually for local serial printer.
        """
        pass

    @abstractmethod
    def _device_status_report(self):
        """
        Reports the cursor position (CPR) to the application as (as though typed at the keyboard)
        ESC[n;mR, where n is the row and m is the column.
        :return: ESC[n;mR, where n is the row and m is the column.
        """
        pass

    @abstractmethod
    def _save_cursor_position(self):
        """
        Saves the cursor position/state.
        """
        pass

    @abstractmethod
    def _restore_cursor_position(self):
        """
        Restores the cursor position/state.
        """
        pass


class ExtendedEscapeSequenceDecoder(EscapeSequenceDecoder):

    def _echo(self, n):
        if n == 0:
            self._echo_off()
        elif n == 1:
            self._echo_on()
        else:
            raise InvalidEscapeSequenceError("n bust be in range 0-1 (inclusive), but was {}".format(n))

    @abstractmethod
    def _echo_off(self):
        pass

    @abstractmethod
    def _echo_on(self):
        pass


class DummyDecoder(EscapeSequenceDecoder):
    sgr_codes = {
        "0": "reset"
        , "1": "bold"
        , "2": "faint"
        , "3": "italic"
        , "4": "underline"
        , "5": "slow blink"
        , "6": "rapid blink"
        , "31": "foreground red"
    }

    def _cursor_up(self, n=1):
        print("Cursor Up ({})".format(n))

    def _cursor_down(self, n=1):
        print("Cursor Down ({})".format(n))

    def _cursor_forward(self, n=1):
        print("Cursor Forward ({})".format(n))

    def _cursor_back(self, n=1):
        print("Cursor Back ({})".format(n))

    def _cursor_next_line(self, n=1):
        print("Cursor Next Line ({})".format(n))

    def _cursor_previous_line(self, n=1):
        print("Cursor Previous Line ({})".format(n))

    def _cursor_horizontal_absolute(self, n=1):
        print("Cursor Horizontal Absolute ({})".format(n))

    def _cursor_position(self, n=1, m=1):
        print("Cursor Position ({}, {})".format(n, m))

    def _erase_in_display(self, n=0):
        arg = {
            0: "clear from cursor to end of screen"
            , 1: "clear from cursor to beginning of the screen"
            , 2: "clear entire screen"
            , 3: "clear entire screen and delete all lines saved in the scrollback buffer"
        }
        try:
            print("Erase in Display ({})".format(arg[n]))
        except KeyError as e:
            raise InvalidEscapeSequenceError("n must be in range 0-3 (inclusive)")

    def _erase_in_line(self, n=0):
        arg = {
            0: "clear from cursor to the end of the line"
            , 1: "clear from cursor to beginning of the line"
            , 2: "clear entire line"
        }
        try:
            print("Erase in Display ({})".format(arg[n]))
        except KeyError as e:
            raise InvalidEscapeSequenceError("n must be in range 0-2 (inclusive)")

    def _scroll_up(self, n=1):
        print("Scroll Up ({})".format(n))

    def _scroll_down(self, n=1):
        print("Scroll Down ({})".format(n))

    def _select_graphic_rendition(self, *n):
        print("Select Graphic Rendition {}".format([DummyDecoder.sgr_codes.get(x) for x in n]))

    def _aux_port_on(self):
        print("AUX Port On")

    def _aux_port_off(self):
        print("AUX Port Off")

    def _device_status_report(self):
        print("Device Status Report")

    def _save_cursor_position(self):
        print("Save Cursor Position")

    def _restore_cursor_position(self):
        print("Restore Cursor Position")

