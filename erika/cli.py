# PYTHON_ARGCOMPLETE_OK
# ^ is about auto-completion, see https://argcomplete.readthedocs.io/en/latest/#global-completion

import os
import sys
from argparse import ArgumentParser
from argparse import RawTextHelpFormatter
from multiprocessing import Process
from multiprocessing import Queue
from queue import Empty

import argcomplete

from erika.TicTacToe import TicTacToe
from erika.erika import Erika
from erika.erika_image_renderer import *
from erika.erika_mock import *

DRY_RUN_WIDTH = 60
DRY_RUN_HEIGHT = 40
DRY_RUN_DELAY = 0.005


def create_argument_parser():
    parser = ArgumentParser(prog='erika.sh',
                            formatter_class=RawTextHelpFormatter,
                            description='Erika type writer connector CLI')
    command_parser = parser.add_subparsers(help='Available commands')
    add_render_demo_parser(command_parser)
    add_render_ascii_art_parser(command_parser)
    add_run_tic_tac_toe_parser(command_parser)
    argcomplete.autocomplete(parser, always_complete_options=True)
    return parser


def add_render_demo_parser(command_parser):
    demo_argument_parser = command_parser.add_parser('demo', help='Do a simple demo')
    demo_argument_parser.set_defaults(func=print_demo)
    add_basic_erika_params(demo_argument_parser)


def add_run_tic_tac_toe_parser(command_parser):
    argument_parser = command_parser.add_parser('tictactoe',
                                                description="""Run the tic tac toe game
                                                
To control the game: 
    * use the WASD keys to move
    * use the space bar to make your mark at the current position
""",
                                                formatter_class=RawTextHelpFormatter,
                                                help='Run the tic tac toe game')
    argument_parser.set_defaults(func=run_tic_tac_toe)
    add_basic_erika_params(argument_parser)


def add_basic_erika_params(argument_parser):
    argument_group = argument_parser.add_mutually_exclusive_group(required=True)
    argument_group.add_argument('--dry-run', '-d',
                                action='store_true',
                                help='If set, will print to standard out instead of connecting to Erika')
    argument_group.add_argument('--serial-port', '-p', metavar='SERIAL_PORT',
                                help='Serial communications port for communicating with the Erika machine.')


def print_demo(args):
    erika = get_erika_for_given_args(args)
    try:
        erika.demo()
    finally:
        erika.wait_for_user_if_simulated()
        erika.__exit__()


def add_render_ascii_art_parser(command_parser):
    render_ascii_art_file_parser = command_parser.add_parser('render_ascii_art',
                                                             aliases=['render_image'],
                                                             formatter_class=RawTextHelpFormatter,
                                                             help='Rendering ASCII art (or a normal image file) in a specified pattern (rendering strategy)',
                                                             description='Rendering ASCII art (or a normal image file) in a specified pattern (rendering strategy)')

    render_ascii_art_file_parser.set_defaults(func=print_ascii_art)
    add_basic_erika_params(render_ascii_art_file_parser)
    render_ascii_art_file_parser.add_argument('--file', '-f', required=False, metavar='FILEPATH', default='-',
                                              help="""File path to the file to print out, containing a pre-rendered ASCII art image.

New: If an image file is referenced instead, will do a monochrome print using "." character and microsteps.
""")
    render_ascii_art_file_parser.add_argument('--strategy', '-s',
                                              choices=['LineByLine', 'Interlaced', 'PerpendicularSpiralInward',
                                                       'RandomDotFill', 'ArchimedeanSpiralOutward'],
                                              default='LineByLine',
                                              help="""Rendering strategy to apply. The value must be one of the following: 
    LineByLine 
        * render the given image line by line
        * default option
    Interlaced
        * render the given image, every even line first (starting count at 0), every odd line later
    PerpendicularSpiralInward ##
        * render the given image, spiralling inward to the middle while going parallel to X or Y axis all the time
    RandomDotFill
        * render the given image, printing one random letter at a time
    ArchimedeanSpiralOutward
        * render the given image, starting from the middle, following an Archimedean spiral as closely as possible""")


def print_ascii_art(args):
    strategy_string = args.strategy
    file_path = args.file
    try:
        if file_path == '-':
            erika = get_erika_for_given_args(args, is_character_based=True)
            renderer = ErikaImageRenderer(erika, strategy_string)
            lines = read_lines_from_stdin_non_blocking()
            renderer.render_lines(lines)
        else:
            erika = get_erika_for_given_args(args)
            renderer = ErikaImageRenderer(erika, strategy_string)
            renderer.render_file(file_path)
    finally:
        if erika:
            erika.wait_for_user_if_simulated()

            # Do a proper shutdown even in case of exception - or curses settings may make the current terminal unusable.
            # I googled - it's okay to call __exit__ directly ( https://stackoverflow.com/a/26635947/1143126 )
            erika.__exit__()


def run_tic_tac_toe(args):
    erika = get_erika_for_given_args(args, is_character_based=True)
    with TicTacToe(erika) as game:
        game.start_game()


def get_erika_for_given_args(args, is_character_based=False):
    is_dry_run = args.dry_run
    com_port = args.serial_port

    if is_dry_run:
        if is_character_based or not 'file' in args:
            # using low size just so it fits on the screen well - does not reflect the paper dimensions that Erika supports
            erika = CharacterBasedErikaMock(DRY_RUN_WIDTH, DRY_RUN_HEIGHT, delay_after_each_step=DRY_RUN_DELAY)
        else:
            # a bit hacky, as I'm mirroring behavior from ErikaImageRenderer - this kindof goes against the now-beautiful architecture :(
            try:
                # hacky: use exception to determine image type
                image_for_provoking_exception = WrappedImage(args.file)
                erika = MicrostepBasedErikaMock(DRY_RUN_WIDTH, DRY_RUN_HEIGHT, delay_after_each_step=DRY_RUN_DELAY)
            except NotAnImageException:
                erika = CharacterBasedErikaMock(DRY_RUN_WIDTH, DRY_RUN_HEIGHT, delay_after_each_step=DRY_RUN_DELAY)

    else:
        erika = Erika(com_port)

    return erika


def read_lines_from_stdin_non_blocking():
    lines = []

    queue_to_pass_lines_through = Queue(maxsize=1)
    worker_process = Process(target=function_for_reading_lines_from_stdin_process,
                             args=(queue_to_pass_lines_through, sys.stdin.fileno()))
    worker_process.start()

    worker_process.join(timeout=0.1)
    has_exited = not worker_process.is_alive()
    if has_exited:
        try:
            lines = queue_to_pass_lines_through.get(block=False)
            return lines
        except Empty as exception:
            raise Exception('unexpected exception') from exception
    else:
        print("no output to generate - provide ASCII art as a file  parameter or on stdin")
        worker_process.terminate()
        sys.exit(1)


def function_for_reading_lines_from_stdin_process(queue_to_pass_lines_through, input_stream_fileno):
    # stdin is closed for new processes :/
    # https://docs.python.org/3.5/library/multiprocessing.html#all-start-methods
    # Note to self: portable :)
    # https://docs.python.org/3/library/os.html#os.fdopen
    input_stream = os.fdopen(input_stream_fileno)

    lines = input_stream.readlines()
    queue_to_pass_lines_through.put(lines)


def main():
    # with argcomplete used now, this shoudl be the very first call - no side-effects should happen before
    argument_parser = create_argument_parser()
    args = argument_parser.parse_args()
    if 'func' in args:
        args.func(args)
    else:
        argument_parser.parse_args('-h')


if __name__ == "__main__":
    main()
