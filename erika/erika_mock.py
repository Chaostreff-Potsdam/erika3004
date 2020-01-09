"""
Record any printing and movement calls to Erika in a 2D array for testing purposes:

This way, rendering algorithms can be tested.
"""
#     x
#     ===>
# y ||
#   ||
#   \/
import curses
import sys
from time import sleep

from erika.erika import AbstractErika
from erika.erika import MICROSTEPS_PER_CHARACTER_HEIGHT
from erika.erika import MICROSTEPS_PER_CHARACTER_WIDTH

"""page dimensions for Erika"""
# tested manually - the cursor will no longer move if a key is pressed
ERIKA_PAGE_WIDTH_CHARACTERS_HARD_LIMIT_AT_12_CHARS_PER_INCH = 74
# tested manually - thee will be a warning "beep" on the next pressed key
ERIKA_PAGE_WIDTH_CHARACTERS_SOFT_LIMIT_AT_12_CHARS_PER_INCH = 65

ERIKA_PAGE_HEIGHT_CHARACTERS = 150

ERIKA_PAGE_WIDTH_MICROSTEPS_HARD_LIMIT_AT_12_CHARS_PER_INCH = ERIKA_PAGE_WIDTH_CHARACTERS_HARD_LIMIT_AT_12_CHARS_PER_INCH * MICROSTEPS_PER_CHARACTER_WIDTH
ERIKA_PAGE_WIDTH_MICROSTEPS_SOFT_LIMIT_AT_12_CHARS_PER_INCH = ERIKA_PAGE_WIDTH_CHARACTERS_SOFT_LIMIT_AT_12_CHARS_PER_INCH * MICROSTEPS_PER_CHARACTER_WIDTH

ERIKA_PAGE_HEIGHT_MICROSTEPS = ERIKA_PAGE_HEIGHT_CHARACTERS * MICROSTEPS_PER_CHARACTER_HEIGHT


class AbstractErikaMock(AbstractErika):

    # TODO are all these methods used?
    # To keep things testable: If the methods make sense for the AbstractErikaMock implementations,
    # add useful test behavior so Erika and AbstractErikaMock are always close!

    def _decode_character(self, char):
        pass

    def _cursor_next_line(self, n=1):
        pass

    def _cursor_previous_line(self, n=1):
        pass

    def _cursor_horizontal_absolute(self, n=1):
        pass

    def _cursor_position(self, n=1, m=1):
        pass

    def _erase_in_display(self, n=0):
        pass

    def _erase_in_line(self, n=0):
        pass

    def _scroll_up(self, n=1):
        pass

    def _scroll_down(self, n=1):
        pass

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

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass

    def alarm(self, duration):
        pass

    def read(self):
        # reading not needed for current tests
        pass

    def _print_raw(self, data):
        raise Exception('User is not supposed to call this function directly')

    def _advance_paper(self):
        raise Exception('User is not supposed to call this function directly')

    def _write_byte(self, data, delay=0.5):
        raise Exception('User is not supposed to call this function directly')

    def set_keyboard_echo(self, value):
        raise Exception('Not supported yet')

    def decode(self, value):
        raise Exception('Not supported yet')


# to get exception-safe behavior, make sure __exit__ is always called (by using with-statements)
class CharacterBasedErikaMock(AbstractErikaMock):

    def __init__(self,
                 width=ERIKA_PAGE_WIDTH_CHARACTERS_SOFT_LIMIT_AT_12_CHARS_PER_INCH,
                 height=ERIKA_PAGE_HEIGHT_CHARACTERS,
                 exception_if_overprinted=True,
                 delay_after_each_step=0,
                 inside_unit_test=False):
        self.inside_unit_test = inside_unit_test

        # if your program fails here, add environment variable TERM=linux
        self.stdscr = curses.initscr()

        self._resize_if_more_space_is_needed(height, width)

        # no enter key needed to post input;
        # can be disabled, it caused error when running print-out-only tests
        if not self.inside_unit_test:
            curses.cbreak()
        curses.nl()

        # escape sequences (numpad, function keys, ...) will be interpreted
        self.stdscr.keypad(True)

        self.stdscr.move(0, 0)

        self.width = width
        self.height = height
        self.canvas = []
        for y in range(height):
            new_list = []
            for x in range(width):
                new_list.append(" ")
            self.canvas.append(new_list)
        self.canvas_x = 0
        self.canvas_y = 0
        self.exception_if_overprinted = exception_if_overprinted
        self.delay_after_each_step = delay_after_each_step

    def __enter__(self):
        return self

    def __exit__(self, *args):
        # caused error when running tests
        if not self.inside_unit_test:
            curses.nocbreak()
        self.stdscr.keypad(False)
        curses.echo()
        # caused error when running tests
        if not self.inside_unit_test:
            curses.endwin()

    def _resize_if_more_space_is_needed(self, height, width):
        window_max_y, window_max_x = self.stdscr.getmaxyx()
        if window_max_x <= (width + 2) or window_max_y <= (height + 2):
            self.stdscr.resize(max(window_max_y, height + 2), max(window_max_x, width + 2))

    def set_keyboard_echo(self, value):
        if value:
            curses.echo()
        else:
            curses.noecho()

    def read(self):
        c = chr(self.stdscr.getch())
        return c

    def wait_for_user_if_simulated(self):
        self.stdscr.getch()

    # microstep-based

    def move_down_microstep(self):
        raise Exception('Microsteps are not supported in character-based tests')

    def move_up_microstep(self):
        raise Exception('Microsteps are not supported in character-based tests')

    def move_right_microsteps(self, num_steps=1):
        raise Exception('Microsteps are not supported in character-based tests')

    def move_left_microsteps(self, num_steps=1):
        raise Exception('Microsteps are not supported in character-based tests')

    def print_pixel(self):
        raise Exception('Microsteps are not supported in character-based tests')

    # character-based

    def move_up(self):
        if not self.inside_unit_test:
            self._cursor_up()
        self.canvas_y -= 1

    def move_down(self):
        if not self.inside_unit_test:
            self._cursor_down()
        self.canvas_y += 1

    def move_left(self):
        if not self.inside_unit_test:
            self._cursor_back()
        self.canvas_x -= 1

    def move_right(self):
        if not self.inside_unit_test:
            self._cursor_forward()
        self.canvas_x += 1

    def _cursor_up(self, n=1):
        y, x = self.stdscr.getyx()
        self.stdscr.move(y - n, x)

    def _cursor_down(self, n=1):
        y, x = self.stdscr.getyx()
        self.stdscr.move(y + n, x)

    def _cursor_forward(self, n=1):
        y, x = self.stdscr.getyx()
        self.stdscr.move(y, x + n)

    def _cursor_back(self, n=1):
        y, x = self.stdscr.getyx()
        self.stdscr.move(y, x - n)

    def demo(self):
        for i in range(0, 10):
            self.move_down()
        self.print_ascii(":)")
        for i in range(0, 10):
            self.move_down()

    def crlf(self):
        self.canvas_x = 0
        self.canvas_y += 1
        y, x = self.stdscr.getyx()
        self.stdscr.move(y + 1, 0)

    def print_ascii(self, text):
        for c in text:
            try:
                # print('Trying to print letter "{}" at ({}, {}).'.format(c, self.canvas_x, self.canvas_y))
                if not self.canvas[self.canvas_y][self.canvas_x] == " ":
                    if self.exception_if_overprinted:
                        raise Exception(
                            "Not supposed to print a letter twice: '{}' at ({}, {})."
                                .format(c, self.canvas_x, self.canvas_y))
                self.canvas[self.canvas_y][self.canvas_x] = c
            except IndexError as e:
                print("IndexError at ({}, {}) of ({}, {}) - increase values of "
                      "cli.DRY_RUN_WIDTH and cli.DRY_RUN_HEIGHT "
                      "if you need more space".format(self.canvas_x, self.canvas_y, self.width, self.height))
                sys.exit(1)

            self.canvas_x += 1
        self.stdscr.addstr(text)
        if self.delay_after_each_step > 0:
            sleep(self.delay_after_each_step)
        self.stdscr.refresh()

    def _test_debug_helper_print_canvas(self):
        """for debugging: print the current canvas to stdout"""
        print(' ' + ''.zfill(self.width).replace('0', '#'))
        for line in self.canvas:
            print('#' + ''.join(line) + '#')
        print(' ' + ''.zfill(self.width).replace('0', '#'))
        print()


# TODO in another ticket: switch MicrostepBasedErikaMock over to using curses
class MicrostepBasedErikaMock(AbstractErikaMock):

    def __init__(self,
                 width=ERIKA_PAGE_WIDTH_MICROSTEPS_HARD_LIMIT_AT_12_CHARS_PER_INCH,
                 height=ERIKA_PAGE_HEIGHT_MICROSTEPS,
                 exception_if_overprinted=True,
                 output_after_each_step=False,
                 delay_after_each_step=0):
        self.width = width
        self.height = height
        self.canvas = []
        for y in range(height):
            new_list = []
            for x in range(width):
                new_list.append(False)
            self.canvas.append(new_list)
        self.canvas_x = 0
        self.canvas_y = 0
        self.exception_if_overprinted = exception_if_overprinted
        self.delay_after_each_step = delay_after_each_step
        self.output_after_each_step = output_after_each_step

    # microstep-based
    def move_down_microstep(self):
        self.canvas_y += 1

    def move_up_microstep(self):
        self.canvas_y -= 1

    def move_right_microsteps(self, num_steps=1):
        self.canvas_x += num_steps

    def move_left_microsteps(self, num_steps=1):
        self.canvas_x -= num_steps

    def print_pixel(self):
        try:
            if self.canvas[self.canvas_y][self.canvas_x]:
                if self.exception_if_overprinted:
                    raise Exception(
                        "Not supposed to print a pixel twice: at ({}, {}).".format(self.canvas_x, self.canvas_y))
            self.canvas[self.canvas_y][self.canvas_x] = True
        except IndexError as e:
            print("IndexError at ({}, {}) of ({}, {}) - increase values of "
                  "cli.DRY_RUN_WIDTH and cli.DRY_RUN_HEIGHT "
                  "if you need more space".format(self.canvas_x, self.canvas_y, self.width, self.height))
            sys.exit(1)
        self.canvas_x += 1

        if self.output_after_each_step:
            self._test_debug_helper_print_canvas()
        if self.delay_after_each_step > 0:
            sleep(self.delay_after_each_step)

    def wait_for_user_if_simulated(self):
        pass

    def _test_debug_helper_print_canvas(self):
        """for debugging: print the current canvas to stdout"""
        print(' ' + ''.zfill(self.width).replace('0', '#'))
        for line in self.canvas:
            print('#' + ''.join(self._transform_for_output(line)) + '#')
        print(' ' + ''.zfill(self.width).replace('0', '#'))
        print()

    def _transform_for_output(self, line):
        return ["X" if x else " " for x in line]

    # character-based

    def move_up(self):
        raise Exception('Characters and character steps are not supported in microstep-based tests')

    def move_down(self):
        raise Exception('Characters and character steps are not supported in microstep-based tests')

    def move_left(self):
        raise Exception('Characters and character steps are not supported in microstep-based tests')

    def move_right(self):
        raise Exception('Characters and character steps are not supported in microstep-based tests')

    def demo(self):
        raise Exception('Characters and character steps are not supported in microstep-based tests')

    def crlf(self):
        raise Exception('Characters and character steps are not supported in microstep-based tests')

    def print_ascii(self, text):
        raise Exception('Characters and character steps are not supported in microstep-based tests')
