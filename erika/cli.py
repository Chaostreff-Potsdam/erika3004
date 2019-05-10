import os
import sys
from argparse import ArgumentParser
from argparse import RawTextHelpFormatter
from multiprocessing import Process
from multiprocessing import Queue
from queue import Empty

from erika.erika import Erika
from erika.erika_image_renderer import *
from erika.erika_mock import *


def create_argument_parser():
    parser = ArgumentParser(prog='erika.sh', description='Erika type writer connector CLI')
    command_parser = parser.add_subparsers(help='Available commands')
    add_render_demo_parser(command_parser)
    add_render_ascii_art_parser(command_parser)
    return parser


def add_render_demo_parser(command_parser):
    demo_argument_parser = command_parser.add_parser('demo', help='Do a simple demo')
    demo_argument_parser.set_defaults(func=print_demo)
    add_basic_erika_params(demo_argument_parser)


def add_basic_erika_params(argument_parser):
    argument_parser.add_argument('--dry-run', '-d',
                                 action='store_true',
                                 help='If set, will print to standard out instead of connecting to Erika')
    argument_parser.add_argument('--serial-port', '-p', required=True, metavar='SERIAL_PORT',
                                 help='Serial communications port for communicating with the Erika machine.')


def print_demo(args):
    erika = get_erika_for_given_args(args)
    erika.demo()


# TODO support using piped input https://docs.python.org/3/library/fileinput.html
def add_render_ascii_art_parser(command_parser):
    render_ascii_art_file_parser = command_parser.add_parser('render_ascii_art',
                                                             formatter_class=RawTextHelpFormatter,
                                                             help='Rendering ASCII art in a specified pattern (rendering strategy)')
    render_ascii_art_file_parser.set_defaults(func=print_ascii_art)
    add_basic_erika_params(render_ascii_art_file_parser)
    render_ascii_art_file_parser.add_argument('--file', '-f', required=False, metavar='FILEPATH', default='-',
                                              help='File path to the file to print out, containing a pre-rendered ASCII art image.')
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
    startegy_string = args.strategy
    file_path = args.file

    if startegy_string == 'LineByLine':
        strategy = strategy = LineByLineErikaImageRenderingStrategy()
    elif startegy_string == 'Interlaced':
        strategy = InterlacedErikaImageRenderingStrategy()
    elif startegy_string == 'PerpendicularSpiralInward':
        strategy = PerpendicularSpiralInwardErikaImageRenderingStrategy()
    elif startegy_string == 'RandomDotFill':
        strategy = RandomDotFillErikaImageRenderingStrategy()
    elif startegy_string == 'ArchimedeanSpiralOutward':
        strategy = ArchimedeanSpiralOutwardErikaImageRenderingStrategy()

    erika = get_erika_for_given_args(args)
    renderer = ErikaImageRenderer(erika, strategy)
    if file_path == '-':
        lines = read_lines_from_stdin_non_blocking()
        renderer.render_ascii_art_lines(lines)
    else:
        renderer.render_ascii_art_file(file_path)


def get_erika_for_given_args(args):
    is_dry_run = args.dry_run
    com_port = args.serial_port

    if is_dry_run:
        # using 60x40 just so it fits on the screen well - does not reflect the paper dimensions that Erika supports
        erika = ErikaMock(60, 40, output_after_each_step=True, delay_after_each_step=0.005)

        # slower, but output will not flicker as much
        # erika = ErikaMock(60, 40, output_after_each_step=True, delay_after_each_step=0.05)
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

    return lines


def function_for_reading_lines_from_stdin_process(queue_to_pass_lines_through, input_stream_fileno):
    # stdin is closed for new processes :/
    # https://docs.python.org/3.5/library/multiprocessing.html#all-start-methods
    # Note to self: portable :)
    # https://docs.python.org/3/library/os.html#os.fdopen
    input_stream = os.fdopen(input_stream_fileno)

    lines = input_stream.readlines()
    queue_to_pass_lines_through.put(lines)


def main():
    argument_parser = create_argument_parser()
    args = argument_parser.parse_args()
    if ('func' in args):
        args.func(args)
    else:
        argument_parser.parse_args('-h')


if __name__ == "__main__":
    main()
