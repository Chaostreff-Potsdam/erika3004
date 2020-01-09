import unittest

from erika.erika_mock import CharacterBasedErikaMock
from erika.erika_mock import MicrostepBasedErikaMock


def assert_print_output(test_case, my_erika, expected_array_of_joined_lines):
    for line in range(len(expected_array_of_joined_lines)):
        expected_line_joined = expected_array_of_joined_lines[line]
        expected_line = list(expected_line_joined)
        actual_line = my_erika.canvas[line]
        test_case.assertEqual(expected_line, actual_line)


def assert_print_output_pixels(test_case, my_erika, expected_array_of_joined_transformed_lines):
    for line in range(len(expected_array_of_joined_transformed_lines)):
        expected_line_joined = expected_array_of_joined_transformed_lines[line]
        expected_line = list(expected_line_joined)
        actual_line = transform_to_printable(my_erika.canvas[line])
        test_case.assertEqual(expected_line, actual_line)


def transform_to_printable(line):
    return ["X" if x else " " for x in line]


class ErikaMockTest(unittest.TestCase):
    def test_write_and_read_back_characters(self):
        """simple test that the CharacterBasedErikaMock records what is written to it"""
        my_erika = CharacterBasedErikaMock(width=5, height=3, inside_unit_test=True)
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
        my_erika = MicrostepBasedErikaMock(width=5, height=3)
        my_erika.print_pixel()
        my_erika.move_right_microsteps(1)
        my_erika.print_pixel()
        my_erika.move_right_microsteps(1)
        my_erika.print_pixel()
        my_erika.move_left_microsteps(1)

        my_erika.move_down_microstep()
        my_erika.move_left_microsteps(3)
        my_erika.print_pixel()
        my_erika.move_right_microsteps(1)
        my_erika.print_pixel()
        my_erika.move_left_microsteps(1)

        my_erika.move_down_microstep()
        my_erika.move_right_microsteps(1)
        my_erika.print_pixel()
        my_erika.move_left_microsteps(3)
        my_erika.print_pixel()
        my_erika.move_left_microsteps(3)
        my_erika.print_pixel()
        my_erika.move_left_microsteps(1)

        my_erika.move_up_microstep()
        my_erika.move_right_microsteps(2)
        my_erika.print_pixel()
        my_erika.move_left_microsteps(1)

        # my_erika._test_debug_helper_print_canvas()
        assert_print_output_pixels(self, my_erika, ["X X X", " XXX ", "X X X"])


def main():
    unittest.main()


if __name__ == '__main__':
    main()
