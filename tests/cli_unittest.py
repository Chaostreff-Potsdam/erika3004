import io
import unittest
import unittest.mock

from erika.cli import create_argument_parser
from erika.cli import print_ascii_art
from erika.cli import print_demo
from erika.cli import run_tic_tac_toe


class CliTest(unittest.TestCase):
    def test_argument_parser_parses_arguments(self):
        """simple test that ArgumentParser will parse the given command line"""
        # arrange
        parser = create_argument_parser()
        self.assertIsNotNone(parser)

        #  act / assert - short form of parameters
        args = parser.parse_args(["render_ascii_art", "-p", "/dev/ttyACM0", "-f", "test_file.txt", "-s",
                                  "PerpendicularSpiralInward"])
        self.assertEqual(args.func, print_ascii_art)
        self.assertFalse(args.dry_run)
        self.assertEqual(args.file, "test_file.txt")
        self.assertEqual(args.serial_port, "/dev/ttyACM0")
        self.assertEqual(args.strategy, "PerpendicularSpiralInward")

        #  act / assert - short form of parameters, dry run
        args = parser.parse_args(["render_ascii_art", "-d", "-f", "test_file.txt", "-s",
                                  "PerpendicularSpiralInward"])
        self.assertEqual(args.func, print_ascii_art)
        self.assertTrue(args.dry_run)
        self.assertEqual(args.file, "test_file.txt")
        self.assertIsNone(args.serial_port)
        self.assertEqual(args.strategy, "PerpendicularSpiralInward")

        #  act / assert - long form of parameters
        args = parser.parse_args(
            ["render_ascii_art", "--serial-port", "/dev/ttyACM0", "--file", "test_file.txt",
             "--strategy", "ArchimedeanSpiralOutward"])
        self.assertEqual(args.func, print_ascii_art)
        self.assertFalse(args.dry_run)
        self.assertEqual(args.file, "test_file.txt")
        self.assertEqual(args.serial_port, "/dev/ttyACM0")
        self.assertEqual(args.strategy, "ArchimedeanSpiralOutward")

        #  act / assert - long form of parameters, dry run
        args = parser.parse_args(
            ["render_ascii_art", "--dry-run", "--file", "test_file.txt",
             "--strategy", "ArchimedeanSpiralOutward"])
        self.assertEqual(args.func, print_ascii_art)
        self.assertTrue(args.dry_run)
        self.assertEqual(args.file, "test_file.txt")
        self.assertIsNone(args.serial_port)
        self.assertEqual(args.strategy, "ArchimedeanSpiralOutward")

        #  act / assert - long form of parameters, dry run, setting flag twice
        args = parser.parse_args(
            ["render_ascii_art", "--dry-run", "-d", "--file", "test_file.txt",
             "--strategy", "ArchimedeanSpiralOutward"])
        self.assertEqual(args.func, print_ascii_art)
        self.assertTrue(args.dry_run)
        self.assertEqual(args.file, "test_file.txt")
        self.assertIsNone(args.serial_port)
        self.assertEqual(args.strategy, "ArchimedeanSpiralOutward")

        #  act / assert - defaults
        args = parser.parse_args(["render_ascii_art", "-p", "COM3"])
        self.assertEqual(args.func, print_ascii_art)
        self.assertFalse(args.dry_run)
        self.assertEqual(args.file, "-")
        self.assertEqual(args.serial_port, "COM3")
        self.assertEqual(args.strategy, "LineByLine")

        #  act / assert - demo mode
        args = parser.parse_args(["demo", "-d"])
        self.assertEqual(args.func, print_demo)
        self.assertTrue(args.dry_run)
        self.assertIsNone(args.serial_port)

    def test_argument_parser_parses_arguments_for_tictactoe(self):
        """simple test that ArgumentParser will parse the given command line"""
        # arrange
        parser = create_argument_parser()
        self.assertIsNotNone(parser)

        #  act / assert - long form of parameters
        args = parser.parse_args(["tictactoe", "--serial-port", "/dev/ttyACM0"])
        self.assertEqual(args.func, run_tic_tac_toe)
        self.assertFalse(args.dry_run)
        self.assertEqual(args.serial_port, "/dev/ttyACM0")

        #  act / assert - repeated / duplicated parameters
        args = parser.parse_args(
            ["tictactoe", "--serial-port", "first", "-p", "second", "--serial-port", "third", "-p", "/dev/ttyACM0"])
        self.assertEqual(args.func, run_tic_tac_toe)
        self.assertFalse(args.dry_run)
        self.assertEqual(args.serial_port, "/dev/ttyACM0")

        #  act / assert - long form of parameters, dry run
        args = parser.parse_args(["tictactoe", "--dry-run"])
        self.assertEqual(args.func, run_tic_tac_toe)
        self.assertTrue(args.dry_run)
        self.assertIsNone(args.serial_port)

        #  act / assert - short form of parameters, real Erika
        args = parser.parse_args(["tictactoe", "-p", "/dev/ttyACM0"])
        self.assertEqual(args.func, run_tic_tac_toe)
        self.assertFalse(args.dry_run)
        self.assertEqual(args.serial_port, "/dev/ttyACM0")

        #  act / assert - short form of parameters, dry run
        args = parser.parse_args(["tictactoe", "-d"])
        self.assertEqual(args.func, run_tic_tac_toe)
        self.assertTrue(args.dry_run)
        self.assertIsNone(args.serial_port)

    def test_argument_parser_prints_help(self):
        """simple test that ArgumentParser will print help text and exit"""
        # arrange
        parser = create_argument_parser()
        self.assertIsNotNone(parser)

        # act / assert
        # https://stackoverflow.com/a/46307456/1143126
        actual_stdout = self.call_parse_args_and_capture_stdout(parser, ["--help"])
        self.assertTrue("-h" in actual_stdout)
        self.assertTrue("--help" in actual_stdout)
        self.assertTrue("erika.sh" in actual_stdout)
        self.assertTrue("render_ascii_art" in actual_stdout)
        self.assertTrue("tictactoe" in actual_stdout)
        self.assertTrue("demo" in actual_stdout)

        # act / assert
        actual_stdout = self.call_parse_args_and_capture_stdout(parser, ["-h"])
        self.assertTrue("-h" in actual_stdout)
        self.assertTrue("--help" in actual_stdout)
        self.assertTrue("erika.sh" in actual_stdout)
        self.assertTrue("render_ascii_art" in actual_stdout)
        self.assertTrue("render_image" in actual_stdout)
        self.assertTrue("tictactoe" in actual_stdout)
        self.assertTrue("demo" in actual_stdout)

        # act / assert
        actual_stdout = self.call_parse_args_and_capture_stdout(parser, ["render_ascii_art", "--help"])
        self.assertTrue("-h" in actual_stdout)
        self.assertTrue("--help" in actual_stdout)
        self.assertTrue("erika.sh render_ascii_art" in actual_stdout)
        self.assertTrue("--file FILEPATH, -f FILEPATH" in actual_stdout)
        self.assertTrue("--dry-run, -d" in actual_stdout)
        self.assertTrue("--serial-port SERIAL_PORT, -p SERIAL_PORT" in actual_stdout)
        self.assertTrue("--strategy" in actual_stdout)
        self.assertTrue("LineByLine" in actual_stdout)
        self.assertTrue("Interlaced" in actual_stdout)
        self.assertTrue("PerpendicularSpiralInward" in actual_stdout)
        self.assertTrue("RandomDotFill" in actual_stdout)
        self.assertTrue("ArchimedeanSpiralOutward" in actual_stdout)

        # act / assert
        actual_stdout = self.call_parse_args_and_capture_stdout(parser, ["render_image", "-h"])
        self.assertTrue("-h" in actual_stdout)
        self.assertTrue("--help" in actual_stdout)
        self.assertTrue("erika.sh render_ascii_art" in actual_stdout)
        self.assertTrue("--file FILEPATH, -f FILEPATH" in actual_stdout)
        self.assertTrue("--dry-run, -d" in actual_stdout)
        self.assertTrue("--serial-port SERIAL_PORT, -p SERIAL_PORT" in actual_stdout)
        self.assertTrue("--strategy" in actual_stdout)
        self.assertTrue("LineByLine" in actual_stdout)
        self.assertTrue("Interlaced" in actual_stdout)
        self.assertTrue("PerpendicularSpiralInward" in actual_stdout)
        self.assertTrue("RandomDotFill" in actual_stdout)
        self.assertTrue("ArchimedeanSpiralOutward" in actual_stdout)

        # act / assert
        actual_stdout = self.call_parse_args_and_capture_stdout(parser, ["demo", "--help"])
        self.assertTrue("-h" in actual_stdout)
        self.assertTrue("--help" in actual_stdout)
        self.assertTrue("erika.sh demo" in actual_stdout)
        self.assertTrue("--dry-run, -d" in actual_stdout)
        self.assertTrue("--serial-port SERIAL_PORT, -p SERIAL_PORT" in actual_stdout)

        # act / assert
        actual_stdout = self.call_parse_args_and_capture_stdout(parser, ["demo", "-h"])
        self.assertTrue("-h" in actual_stdout)
        self.assertTrue("--help" in actual_stdout)
        self.assertTrue("erika.sh demo" in actual_stdout)
        self.assertTrue("--dry-run, -d" in actual_stdout)
        self.assertTrue("--serial-port SERIAL_PORT, -p SERIAL_PORT" in actual_stdout)

        # act / assert
        actual_stdout = self.call_parse_args_and_capture_stdout(parser, ["tictactoe", "-h"])
        self.assertTrue("-h" in actual_stdout)
        self.assertTrue("--help" in actual_stdout)
        self.assertTrue("erika.sh tictactoe" in actual_stdout)
        self.assertTrue("--dry-run, -d" in actual_stdout)
        self.assertTrue("--serial-port SERIAL_PORT, -p SERIAL_PORT" in actual_stdout)

    @unittest.mock.patch('sys.stdout', new_callable=io.StringIO)
    def call_parse_args_and_capture_stdout(self, parser, args, mock_stdout):
        self.assertRaises(SystemExit, parser.parse_args, args)
        return mock_stdout.getvalue()

    def test_argument_parser_invalid_arguments(self):
        # arrange
        parser = create_argument_parser()
        self.assertIsNotNone(parser)

        # act / assert
        actual_stdout = self.call_parse_args_expecting_exception(parser, ["render_image", "-d", "-s", "port"])
        self.assertTrue("error" in actual_stdout)
        self.assertTrue("invalid choice" in actual_stdout)

        actual_stdout = self.call_parse_args_expecting_exception(parser, ["render_image", "-nonexistent"])
        self.assertTrue("error" in actual_stdout)
        self.assertTrue("one of the arguments" in actual_stdout)
        self.assertTrue("is required" in actual_stdout)

        actual_stdout = self.call_parse_args_expecting_exception(parser, ["render_image", "-d", "-nonexistent"])
        self.assertTrue("error" in actual_stdout)
        self.assertTrue("unrecognized arguments" in actual_stdout)
        self.assertTrue("-nonexistent" in actual_stdout)

    @unittest.mock.patch('sys.stderr', new_callable=io.StringIO)
    def call_parse_args_expecting_exception(self, parser, args, mock_stderr):
        with self.assertRaises(SystemExit) as context_manager:
            parsed_args = parser.parse_args(args)
            print(parsed_args)
        system_exit = context_manager.exception
        self.assertEqual(system_exit.code, 2)
        return mock_stderr.getvalue()


def main():
    unittest.main()


if __name__ == '__main__':
    main()
