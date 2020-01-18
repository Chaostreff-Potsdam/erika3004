import unittest

from erika.erika_mock import CharacterBasedErikaMock
from erika.erika_mock import MicrostepBasedErikaMock


def assert_print_output(test_case, my_erika, expected_array_of_joined_lines):
    for line in range(len(expected_array_of_joined_lines)):
        expected_line_joined = expected_array_of_joined_lines[line]
        expected_line = list(expected_line_joined)
        actual_line = my_erika.canvas[line]
        test_case.assertEqual(expected_line, actual_line)

    # validate curses output as well
    y, x = my_erika.stdscr.getyx()
    my_erika.stdscr.move(0, 0)
    temp_y = 0
    for line in range(len(expected_array_of_joined_lines)):
        expected_line_joined = expected_array_of_joined_lines[line]
        expected_line_encoded = expected_line_joined.encode()
        actual_line_encoded = my_erika.stdscr.instr(temp_y, 0, len(expected_line_encoded))
        test_case.assertEqual(expected_line_encoded, actual_line_encoded)
        temp_y += 1
    my_erika.stdscr.move(y, x)


class ErikaMockTest(unittest.TestCase):
    def test_write_and_read_back_characters(self):
        """simple test that the CharacterBasedErikaMock records what is written to it"""
        my_erika = CharacterBasedErikaMock(width=5, height=3, inside_unit_test=True, exception_if_overprinted=True)
        my_erika.print_ascii("Hello")
        my_erika.move_down()
        my_erika.move_down()
        my_erika.move_left()
        my_erika.move_left()
        my_erika.move_left()
        my_erika.print_ascii("!")
        my_erika.move_up()
        my_erika.move_left()
        my_erika.move_left()
        my_erika.move_left()
        my_erika.print_ascii("World")
        # my_erika.test_debug_helper_print_canvas()
        assert_print_output(self, my_erika, ["Hello", "World", "  !  "])

    def test_write_and_read_back_microsteps(self):
        my_erika = MicrostepBasedErikaMock(width=5, height=3, inside_unit_test=True)
        my_erika.print_pixel()
        my_erika.move_right_microsteps(1)
        my_erika.print_pixel()
        my_erika.move_right_microsteps(1)
        my_erika.print_pixel()
        my_erika.move_left_microsteps(1)
        assert_print_output(self, my_erika, ["X X X", "     ", "     "])

        my_erika.move_down_microstep()
        my_erika.move_left_microsteps(3)
        my_erika.print_pixel()
        my_erika.move_right_microsteps(1)
        my_erika.print_pixel()
        my_erika.move_left_microsteps(1)
        assert_print_output(self, my_erika, ["X X X", " X X ", "     "])

        my_erika.move_down_microstep()
        my_erika.move_right_microsteps(1)
        my_erika.print_pixel()
        my_erika.move_left_microsteps(3)
        my_erika.print_pixel()
        my_erika.move_left_microsteps(3)
        my_erika.print_pixel()
        my_erika.move_left_microsteps(1)
        assert_print_output(self, my_erika, ["X X X", " X X ", "X X X"])

        my_erika.move_up_microstep()
        my_erika.move_right_microsteps(2)
        my_erika.print_pixel()
        my_erika.move_left_microsteps(1)
        assert_print_output(self, my_erika, ["X X X", " XXX ", "X X X"])

    def test_delete_ascii(self):
        my_erika = CharacterBasedErikaMock(width=5, height=1, inside_unit_test=True, exception_if_overprinted=False)
        my_erika.print_ascii("Hello")
        assert_print_output(self, my_erika, ["Hello"])

        # test that deletion of 1 character works
        my_erika.delete_ascii("o")
        assert_print_output(self, my_erika, ["Hell "])

        # test that deletion of a reversed string of characters works
        my_erika.delete_ascii("lle")
        assert_print_output(self, my_erika, ["H    "])

        # test that the cursor rests above the "H" now
        my_erika.print_ascii("elp")
        assert_print_output(self, my_erika, ["Help "])

    def test_delete_ascii2(self):
        my_erika = CharacterBasedErikaMock(width=5, height=1, inside_unit_test=True, exception_if_overprinted=False)
        my_erika.print_ascii("Hello")
        assert_print_output(self, my_erika, ["Hello"])

        # test that deletion of 1 character works
        my_erika.move_left()
        my_erika.delete_ascii("lle")
        assert_print_output(self, my_erika, ["H   o"])

        my_erika.move_right()
        my_erika.print_ascii("x")
        assert_print_output(self, my_erika, ["H x o"])

    def test_delete_pixel(self):
        my_erika = MicrostepBasedErikaMock(width=5, height=1, inside_unit_test=True, exception_if_overprinted=False)
        my_erika.print_pixel()
        my_erika.print_pixel()
        my_erika.print_pixel()
        my_erika.print_pixel()
        my_erika.print_pixel()
        assert_print_output(self, my_erika, ["XXXXX"])

        my_erika.move_left_microsteps(1)
        my_erika.delete_pixel()
        assert_print_output(self, my_erika, ["XXX X"])


def main():
    unittest.main()


if __name__ == '__main__':
    main()
