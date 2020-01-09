# coding=utf-8

import unittest

from erika.erika_image_renderer import *
from erika.erika_mock import *
from tests.erika_mock_unittest import assert_print_output
from tests.erika_mock_unittest import assert_print_output_pixels


# noinspection SpellCheckingInspection
class RendererTest(unittest.TestCase):

    def helper_test_ErikaImageRenderingStrategy_square(self, strategy):
        """test helper to verify rendering with the given strategy works"""
        with CharacterBasedErikaMock(6, 6, inside_unit_test=True) as my_erika:
            renderer = ErikaImageRenderer(my_erika, "test: strategy will be set explicitly")
            renderer.render_file_for_fixed_strategy('tests/test_resources/test_ascii_art_small.txt', strategy)
            assert_print_output(self, my_erika, ["abcdef", "ghijkl", "mnopqr", "stuvwx", "yzäöüß", "!?#'\"/"])

    def helper_test_ErikaImageRenderingStrategy_high(self, strategy):
        """test helper to verify rendering with the given strategy works"""
        with CharacterBasedErikaMock(3, 12, inside_unit_test=True) as my_erika:
            renderer = ErikaImageRenderer(my_erika, "test: strategy will be set explicitly")
            renderer.render_file_for_fixed_strategy('tests/test_resources/test_ascii_art_small_high.txt', strategy)
            assert_print_output(self, my_erika,
                                ["abc", "def", "ghi", "jkl", "mno", "pqr", "stu", "vwx", "yzä", "öüß", "!?#", "'\"/"])

    def helper_test_ErikaImageRenderingStrategy_wide(self, strategy):
        """test helper to verify rendering with the given strategy works"""
        with CharacterBasedErikaMock(9, 4, inside_unit_test=True) as my_erika:
            renderer = ErikaImageRenderer(my_erika, "test: strategy will be set explicitly")
            renderer.render_file_for_fixed_strategy('tests/test_resources/test_ascii_art_small_wide.txt', strategy)
            assert_print_output(self, my_erika, ["abcdefghi", "jklmnopqr", "stuvwxyzä"])

    def helper_test_ErikaImageRenderingStrategy_real_image(self, strategy):
        """test helper to verify rendering with the given strategy works"""
        with MicrostepBasedErikaMock(20, 30) as my_erika:
            renderer = ErikaImageRenderer(my_erika, "test: strategy will be set explicitly")
            renderer.render_file_for_fixed_strategy('tests/test_resources/test_image_grayscale_1.bmp', strategy)
            assert_print_output_pixels(self, my_erika, [
                "XXXXXXXXXXXXXXXXXXXX",
                "XXXXXXXXXXXXXXXXXXXX",
                "XXXXXXXXXXXXXXXXXXXX",
                "XXXXXXXXXXXXXXXXXXXX",
                "XXXXXXXXXXXXXXXXXXXX",
                "XXXXXXXXXXXXXXXXXXXX",
                "XXXXXXXXXXXXXXXXXXXX",
                "                    ",
                "                    ",
                "                    ",
                "                    ",
                "                    ",
                "                    ",
                "                    ",
                "                    ",
                "                    ",
                "                    ",
                "                    ",
                "                    ",
                "                    ",
                "                    ",
                "                    ",
                "XXXXXXXXXXXXXXXXXXXX",
                "XXXXXXXXXXXXXXXXXXXX",
                "XXXXXXXXXXXXXXXXXXXX",
                "XXXXXXXXXXXXXXXXXXXX",
                "XXXXXXXXXXXXXXXXXXXX",
                "XXXXXXXXXXXXXXXXXXXX",
                "XXXXXXXXXXXXXXXXXXXX",
                "XXXXXXXXXXXXXXXXXXXX"
            ])

    def testLineByLineErikaImageRenderingStrategy(self):
        """simple test that printing line by line works"""
        strategy = LineByLineErikaImageRenderingStrategy()
        self.helper_test_ErikaImageRenderingStrategy_square(strategy)
        self.helper_test_ErikaImageRenderingStrategy_high(strategy)
        self.helper_test_ErikaImageRenderingStrategy_wide(strategy)
        self.helper_test_ErikaImageRenderingStrategy_real_image(strategy)

    def testInterlacedErikaImageRenderingStrategy(self):
        """simple test that printing odd-then-even lines works"""
        strategy = InterlacedErikaImageRenderingStrategy()
        self.helper_test_ErikaImageRenderingStrategy_square(strategy)
        self.helper_test_ErikaImageRenderingStrategy_high(strategy)
        self.helper_test_ErikaImageRenderingStrategy_wide(strategy)
        self.helper_test_ErikaImageRenderingStrategy_real_image(strategy)

    def testPerpendicularSpiralInwardErikaImageRenderingStrategy(self):
        """simple test that printing as a perpendicular spiral inward works"""
        strategy = PerpendicularSpiralInwardErikaImageRenderingStrategy()
        self.helper_test_ErikaImageRenderingStrategy_square(strategy)
        self.helper_test_ErikaImageRenderingStrategy_high(strategy)
        self.helper_test_ErikaImageRenderingStrategy_wide(strategy)
        self.helper_test_ErikaImageRenderingStrategy_real_image(strategy)

    def testRandomDotFillErikaImageRenderingStrategy(self):
        """simple test that printing as one random dot at a time works"""
        strategy = RandomDotFillErikaImageRenderingStrategy()
        self.helper_test_ErikaImageRenderingStrategy_square(strategy)
        self.helper_test_ErikaImageRenderingStrategy_high(strategy)
        self.helper_test_ErikaImageRenderingStrategy_wide(strategy)
        self.helper_test_ErikaImageRenderingStrategy_real_image(strategy)

    def testArchimedeanSpiralOutwardErikaImageRenderingStrategy(self):
        """simple test that printing following along an archimedean spiral works"""
        strategy = ArchimedeanSpiralOutwardErikaImageRenderingStrategy()
        self.helper_test_ErikaImageRenderingStrategy_square(strategy)
        self.helper_test_ErikaImageRenderingStrategy_high(strategy)
        self.helper_test_ErikaImageRenderingStrategy_wide(strategy)
        self.helper_test_ErikaImageRenderingStrategy_real_image(strategy)

    def testArchimedeanSpiralOutwardErikaImageRenderingStrategy2(self):
        """test with a bigger file + two spirals"""
        with CharacterBasedErikaMock(60, 30, False, inside_unit_test=True) as my_erika:
            strategy = ArchimedeanSpiralOutwardErikaImageRenderingStrategy(spiral_param_a=1,
                                                                           render_remaining_characters=False)
            renderer = ErikaImageRenderer(my_erika, "test: strategy will be set explicitly")
            renderer.render_file_for_fixed_strategy('tests/test_resources/test_ascii_art.txt', strategy)
            # my_erika.test_debug_helper_print_canvas()

            strategy2 = ArchimedeanSpiralOutwardErikaImageRenderingStrategy(spiral_param_a=0.5,
                                                                            render_remaining_characters=False)
            renderer.render_file_for_fixed_strategy('tests/test_resources/test_ascii_art.txt', strategy2)
            # my_erika.test_debug_helper_print_canvas()


def main():
    unittest.main()


if __name__ == '__main__':
    main()
