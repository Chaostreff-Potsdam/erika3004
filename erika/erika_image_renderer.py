import math
import random
from enum import Enum

from erika.image_converter import WrappedImage, NotAnImageException


class Direction(Enum):
    NORTHEAST = 1
    NORTHWEST = 2
    SOUTHEAST = 3
    SOUTHWEST = 4


class ErikaImageRenderer:
    def __init__(self, some_erika, rendering_strategy_string):
        self.erika = some_erika
        self.strategy_string = rendering_strategy_string

    def render_file(self, file_path):
        strategy = self.create_strategy()
        self.render_file_for_fixed_strategy(file_path, strategy)

    def render_file_for_fixed_strategy(self, file_path, strategy):
        erika_image_abstraction = ErikaAndInputFacadeFactory.create_for_path(self.erika, file_path)
        strategy.render(erika_image_abstraction)

    def render_lines(self, lines):
        strategy = self.create_strategy()
        self.render_lines_for_fixed_strategy(lines, strategy)

    def render_lines_for_fixed_strategy(self, lines, strategy):
        erika_image_abstraction = ErikaAndInputFacadeFactory.create_for_lines(self.erika, lines)
        strategy.render(erika_image_abstraction)

    def create_strategy(self):
        strategies = {
            'LineByLine': LineByLineErikaImageRenderingStrategy,
            'Interlaced': InterlacedErikaImageRenderingStrategy,
            'PerpendicularSpiralInward': PerpendicularSpiralInwardErikaImageRenderingStrategy,
            'RandomDotFill': RandomDotFillErikaImageRenderingStrategy,
            'ArchimedeanSpiralOutward': ArchimedeanSpiralOutwardErikaImageRenderingStrategy
        }
        return strategies[self.strategy_string]()


class ErikaImageRenderingStrategy:

    def __init__(self):
        pass

    def render(self, erika_image_abstraction):
        raise Exception('Not implemented')

    @staticmethod
    def _generate_coordinates(range_x_upper, range_y_upper, range_x_lower=0, range_y_lower=0):
        for x in range(range_x_lower, range_x_upper):
            for y in range(range_y_lower, range_y_upper):
                yield (x, y)

    def _initialize_printed_characters_map(self, max_line_length, line_count):
        self.printed = []
        for y in range(line_count):
            new_row = []
            for x in range(max_line_length):
                new_row.append(False)
            self.printed.append(new_row)


class LineByLineErikaImageRenderingStrategy(ErikaImageRenderingStrategy):

    def __init__(self):
        ErikaImageRenderingStrategy.__init__(self)

    def render(self, erika_image_abstraction):
        for y in range(0, erika_image_abstraction.height()):
            erika_image_abstraction.print_line_at(y)
            erika_image_abstraction.crlf()


class InterlacedErikaImageRenderingStrategy(ErikaImageRenderingStrategy):

    def __init__(self):
        ErikaImageRenderingStrategy.__init__(self)

    def render(self, erika_image_abstraction):
        line_count = erika_image_abstraction.height()
        moved = 0
        for even in range(0, line_count, 2):
            erika_image_abstraction.print_line_at(even)
            erika_image_abstraction.crlf()
            erika_image_abstraction.crlf()
            moved += 2

        # reset cursor to start of line
        erika_image_abstraction.crlf()

        # do not compensate the line that this adds - the extra line will position the cursor right where we want it
        # erika_image_abstraction.move_up()

        for lines_to_move_up in range(0, moved):
            erika_image_abstraction.move_up()

        for odd in range(1, line_count, 2):
            erika_image_abstraction.print_line_at(odd)
            erika_image_abstraction.crlf()
            erika_image_abstraction.crlf()


class PerpendicularSpiralInwardErikaImageRenderingStrategy(ErikaImageRenderingStrategy):

    def __init__(self):
        ErikaImageRenderingStrategy.__init__(self)

    def render(self, erika_image_abstraction):
        line_count = erika_image_abstraction.height()
        max_line_length = erika_image_abstraction.width()
        self._print_spiral_recursively(erika_image_abstraction, 0, 0, max_line_length - 1, line_count - 1)

    def _print_spiral_recursively(self, erika_image_abstraction,
                                  upper_left_x, upper_left_y,
                                  lower_right_x, lower_right_y):
        """ASSUMPTION: current position is at (upper_left_x, upper_left_y)"""
        if upper_left_x > lower_right_x or upper_left_y > lower_right_y:
            return

        # render one round of the spiral, clockwise

        #
        # =====>
        #
        for x in range(upper_left_x, lower_right_x + 1):
            erika_image_abstraction.print_at(x, upper_left_y)

        # edge case: this was the only last row
        if upper_left_y == lower_right_y:
            return

        # reset to last cursor position
        erika_image_abstraction.move_left()

        # go down - do not print a character twice
        erika_image_abstraction.move_down()

        # ||
        # ||
        # \/
        for y in range(upper_left_y + 1, lower_right_y):
            erika_image_abstraction.print_at(lower_right_x, y)
            erika_image_abstraction.move_down()
            erika_image_abstraction.move_left()

        # special handling of last character - smoothen transition
        erika_image_abstraction.print_at(lower_right_x, lower_right_y)

        # edge case: this was the only last column
        if upper_left_x == lower_right_x:
            return

        # back to last printed character
        erika_image_abstraction.move_left()
        erika_image_abstraction.move_left()

        #
        # <=====
        #
        for x in range(lower_right_x - 1, upper_left_x, -1):
            erika_image_abstraction.print_at(x, lower_right_y)
            erika_image_abstraction.move_left()
            erika_image_abstraction.move_left()

        # make this a separate step - curses will fail if this would go off screen
        for x in range(upper_left_x, upper_left_x - 1, -1):
            erika_image_abstraction.print_at(x, lower_right_y)
            erika_image_abstraction.move_left()

        erika_image_abstraction.move_up()

        # /\
        # ||
        # ||
        for y in range(lower_right_y - 1, upper_left_y + 1, -1):
            erika_image_abstraction.print_at(upper_left_x, y)
            erika_image_abstraction.move_up()
            erika_image_abstraction.move_left()

        # special handling of last character - smoothen transition
        if lower_right_y - 1 >= upper_left_y + 1:
            erika_image_abstraction.print_at(upper_left_x, upper_left_y + 1)

        # continue with smaller spiral - restart recursion
        self._print_spiral_recursively(erika_image_abstraction,
                                       upper_left_x + 1, upper_left_y + 1,
                                       lower_right_x - 1, lower_right_y - 1)


class RandomDotFillErikaImageRenderingStrategy(ErikaImageRenderingStrategy):

    def __init__(self):
        ErikaImageRenderingStrategy.__init__(self)
        self.current_x = 0
        self.current_y = 0

    def render(self, erika_image_abstraction):
        self.current_x = 0
        self.current_y = 0

        line_count = erika_image_abstraction.height()
        max_line_length = erika_image_abstraction.width()
        self._initialize_printed_characters_map(max_line_length, line_count)
        self._render_random_dots_naive(line_count, max_line_length, erika_image_abstraction)

    # naive approach: generate random position, render if not yet printed there
    # * this results in about 100 additional re-generation attempts for random numbers for the small test images
    # * improvement idea:
    # ** define a cut-off point (e.g. "if 100 letters left")
    # ** add remaining dots to a list + use random.choice(list) on those instead of continuing to guess blindly
    def _render_random_dots_naive(self, line_count, max_line_length, erika_image_abstraction):
        # once more, assuming a square image
        number_of_characters = line_count * max_line_length

        for i in range(0, number_of_characters):
            # generate random position
            # look up if already printed - re-generate until empty space was found
            position_x, position_y = self._generate_random_position(max_line_length, line_count)
            while self.printed[position_y][position_x]:
                position_x, position_y = self._generate_random_position(max_line_length, line_count)

            # move there + print
            self._move_to(erika_image_abstraction, position_x, position_y)

            erika_image_abstraction.print_at(position_x, position_y)
            self.current_x += 1
            self.printed[position_y][position_x] = True
            # repeat

    @staticmethod
    def _generate_random_position(exclusive_max_x, exclusive_max_y):
        random1 = random.randint(0, exclusive_max_x - 1)
        random2 = random.randint(0, exclusive_max_y - 1)
        return random1, random2

    def _move_to(self, erika_image_abstraction, position_x, position_y):
        # naive: adjust X position first, then Y position
        while self.current_x < position_x:
            erika_image_abstraction.move_right()
            self.current_x += 1

        while position_x < self.current_x:
            erika_image_abstraction.move_left()
            self.current_x -= 1

        while self.current_y < position_y:
            erika_image_abstraction.move_down()
            self.current_y += 1

        while position_y < self.current_y:
            erika_image_abstraction.move_up()
            self.current_y -= 1


class ArchimedeanSpiralOutwardErikaImageRenderingStrategy(ErikaImageRenderingStrategy):

    # TODO mention "This is a reST style." in commit message + link to https://stackoverflow.com/a/24385103/1143126
    def __init__(self, spiral_param_a=1, spiral_param_b=0.35, spiral_step_size=0.01, render_remaining_characters=True):
        """
        "...with real numbers a and b.

        Changing the parameter a turns the spiral,

        while b controls the distance between successive turnings."

        https://en.wikipedia.org/wiki/Archimedean_spiral

        :param spiral_param_a: turns the spiral
        :param spiral_param_b: controls distance between spiral turns
        :param spiral_step_size: step size between successive datapoints
        :param render_remaining_characters: if False, will only render the spiral, not fill remaining gaps later
        """
        ErikaImageRenderingStrategy.__init__(self)

        self.spiral_param_a = spiral_param_a
        self.spiral_param_b = spiral_param_b

        # round spiral:
        # 1 / 20 * pi
        # 1 / 10
        #
        # jagged spiral:
        # 1
        self.spiral_step_size = spiral_step_size

        # tolerance around 45° angle (in all directions) to mark as area for cut-off
        self.CUTOFF_ANGLE_TOLERANCE = 15

        self.render_remaining_characters = render_remaining_characters

        # init - only used later
        self.current_x = 0
        self.current_y = 0
        self.spiral_offset_x = 0
        self.spiral_offset_y = 0

    def render(self, erika_image_abstraction):
        self.current_x = 0
        self.current_y = 0

        line_count = erika_image_abstraction.height()
        max_line_length = erika_image_abstraction.width()
        self._initialize_printed_characters_map(max_line_length, line_count)

        self._render_spiral(erika_image_abstraction, max_line_length, line_count)

        if self.render_remaining_characters:
            self._render_remaining(erika_image_abstraction, max_line_length, line_count)

        self._reset_to_upper_left(erika_image_abstraction)

    # Formula for Archimedean spiral:
    # https://en.wikipedia.org/wiki/Archimedean_spiral
    # r = a + b * phi
    # (with phi replaced later by t = 0, 1, ...)
    #
    # from polar coordinates to cartesian coordinates:
    # x = r * cos(phi)
    # y = r * sin(phi)
    #
    # follows:
    # r = x / cos(phi)
    # x / cos(phi) = a + b * phi
    # x = (a + b * phi) * cos(phi)
    #
    # r = y / sin(phi)
    # y / sin(phi) = a + b * phi
    # y = (a + b * phi) * sin(phi)
    #
    def _render_spiral(self, erika_image_abstraction, max_line_length, line_count):

        max_x = max_line_length - 1
        max_y = line_count - 1

        i = 1
        directions_out_of_bounds = {}
        self.spiral_offset_x = math.floor(max_x / 2)
        self.spiral_offset_y = math.floor(max_y / 2)
        self._move_to(erika_image_abstraction, self.spiral_offset_x, self.spiral_offset_y)
        while True:
            t = i * self.spiral_step_size

            x = (self.spiral_param_a + self.spiral_param_b * t) * math.cos(t) + self.spiral_offset_x
            y = (self.spiral_param_a + self.spiral_param_b * t) * math.sin(t) + self.spiral_offset_y

            # cut off: cut off if turtle is in the corner (close to 45 degree angle in all directions) + out of bounds
            current_angle = (math.degrees(t) % 360)
            if ((45 - self.CUTOFF_ANGLE_TOLERANCE <= current_angle)
                    and (current_angle <= 45 + self.CUTOFF_ANGLE_TOLERANCE)):
                self._note_if_out_of_bounds(directions_out_of_bounds, Direction.NORTHEAST, max_x, max_y, x, y)
            if ((135 - self.CUTOFF_ANGLE_TOLERANCE <= current_angle)
                    and (current_angle <= 135 + self.CUTOFF_ANGLE_TOLERANCE)):
                self._note_if_out_of_bounds(directions_out_of_bounds, Direction.NORTHWEST, max_x, max_y, x, y)
            if ((225 - self.CUTOFF_ANGLE_TOLERANCE <= current_angle)
                    and (current_angle <= 225 + self.CUTOFF_ANGLE_TOLERANCE)):
                self._note_if_out_of_bounds(directions_out_of_bounds, Direction.SOUTHEAST, max_x, max_y, x, y)
            if ((315 - self.CUTOFF_ANGLE_TOLERANCE <= current_angle)
                    and (current_angle <= 315 + self.CUTOFF_ANGLE_TOLERANCE)):
                self._note_if_out_of_bounds(directions_out_of_bounds, Direction.SOUTHWEST, max_x, max_y, x, y)

            # all 4 directions are out of bounds now
            if len(directions_out_of_bounds) > 3:
                break

            rounded_x = math.floor(x)
            rounded_y = math.floor(y)
            # move to calculated next point + print
            self._goto_and_print_if_in_bounds(erika_image_abstraction, max_x, max_y, rounded_x, rounded_y)

            i += 1

    @staticmethod
    def _note_if_out_of_bounds(directions_out_of_bounds, direction, max_x, max_y, x, y):
        if (x < 0) or (y < 0) or (max_x < x) or (max_y < y):
            directions_out_of_bounds[direction] = 1

    def _goto_and_print_if_in_bounds(self, erika_image_abstraction, max_x, max_y, x, y):
        if (x < 0) or (y < 0) or (max_x < x) or (max_y < y):
            return
        self._goto_and_print(erika_image_abstraction, x, y)

    def _goto_and_print(self, erika_image_abstraction, x, y):
        if self.printed[y][x]:
            return

        self.printed[y][x] = True
        self._move_to(erika_image_abstraction, x, y)
        erika_image_abstraction.print_at(x, y)
        self.current_x += 1

    # TODO dry
    def _move_to(self, erika_image_abstraction, position_x, position_y):
        # naive: adjust X position first, then Y position
        while self.current_x < position_x:
            erika_image_abstraction.move_right()
            self.current_x += 1

        while position_x < self.current_x:
            erika_image_abstraction.move_left()
            self.current_x -= 1

        while self.current_y < position_y:
            erika_image_abstraction.move_down()
            self.current_y += 1

        while position_y < self.current_y:
            erika_image_abstraction.move_up()
            self.current_y -= 1

    def _render_remaining(self, erika_image_abstraction, max_line_length, line_count):
        # render remaining letters in ascending order of distance to middle point
        found = True
        while found:
            found = False
            min_distance = float("inf")
            min_position_x = 0
            min_position_y = 0

            for x, y in self._generate_coordinates(max_line_length, line_count):
                is_printed = self.printed[y][x]
                is_new_min_distance = self._distance_to_spiral_center(x, y) < min_distance
                if is_new_min_distance and not is_printed:
                    found = True
                    min_position_x = x
                    min_position_y = y
                    min_distance = self._distance_to_spiral_center(x, y)
            if found:
                self._goto_and_print(erika_image_abstraction, min_position_x, min_position_y)

    def _distance_to_spiral_center(self, x, y):
        delta_x = math.fabs(self.spiral_offset_x - x)
        delta_y = math.fabs(self.spiral_offset_y - y)
        return math.sqrt(delta_x * delta_x + delta_y * delta_y)

    def _reset_to_upper_left(self, erika_image_abstraction):
        self._move_to(erika_image_abstraction, 0, 0)


class ErikaAndInputFacadeFactory:

    @classmethod
    def create_for_path(cls, erika, file_path):
        try:
            image = WrappedImage(file_path)
            return ErikaAndImageInputFacade(erika, image)
        except NotAnImageException:
            lines = _read_lines_without_trailing_newlines(file_path)
            return ErikaAndAsciiArtInputFacade(erika, lines)

    @classmethod
    def create_for_lines(cls, erika, lines):
        return ErikaAndAsciiArtInputFacade(erika, lines)


class ErikaAndInputFacade:

    def move_left(self):
        pass

    def move_right(self):
        pass

    def move_up(self):
        pass

    def move_down(self):
        pass

    def crlf(self):
        pass

    def print_at(self, x, y):
        pass

    def print_line_at(self, y):
        pass

    def print_whole_line(self, line):
        pass


class ErikaAndAsciiArtInputFacade(ErikaAndInputFacade):

    def __init__(self, erika, lines):
        """
        Indirection for rendering ASCII art images - hiding the concrete type of image from the rendering strategy.
        :param erika an Erika instance (or test double)
        :param lines ASCII art image's text lines
        """
        self.erika = erika
        self.lines = lines

    def move_left(self):
        self.erika.move_left()

    def move_right(self):
        self.erika.move_right()

    def move_up(self):
        self.erika.move_up()

    def move_down(self):
        self.erika.move_down()

    def crlf(self):
        self.erika.crlf()

    def print_at(self, x, y):
        self.erika.print_ascii(self.lines[y][x])

    def print_line_at(self, y):
        self.erika.print_ascii(self.lines[y])

    def height(self):
        return len(self.lines)

    def width(self):
        return self._calculate_max_line_length(self.lines)

    @staticmethod
    def _calculate_max_line_length(lines):
        max_length = 0
        for line in lines:
            if len(line) > max_length:
                max_length = len(line)
        return max_length


class ErikaAndImageInputFacade(ErikaAndInputFacade):

    def __init__(self, erika, wrapped_image):
        """
        Indirection for rendering ASCII art images - hiding the concrete type of image from the rendering strategy.
        :param erika an Erika instance (or test double)
        :param wrapped_image a WrappedImage abstracting from the image data
        """
        self.erika = erika
        self.wrapped_image = wrapped_image

        # because we can't rely on the crlf command, we need to keep track of
        # the position along the X axis for supporting "newline" for image output
        self.position_x = 0

    def move_left(self):
        self.erika.move_left_microsteps(1)
        self.position_x -= 1

    def move_right(self):
        self.erika.move_right_microsteps(1)
        self.position_x += 1

    def move_up(self):
        self.erika.move_up_microstep()

    def move_down(self):
        self.erika.move_down_microstep()

    def crlf(self):
        self.erika.move_left_microsteps(self.position_x)
        self.position_x = 0
        self.erika.move_down_microstep()

    def print_at(self, x, y):
        if self.wrapped_image.is_pixel_set(x, y):
            self.erika.print_pixel()
        else:
            self.erika.move_right_microsteps(1)
        self.position_x += 1

    def print_line_at(self, y):
        for x in range(0, self.wrapped_image.width()):
            self.print_at(x, y)

    def height(self):
        return self.wrapped_image.height()

    def width(self):
        return self.wrapped_image.width()


def _read_lines_without_trailing_newlines(file_path):
    with open(file_path, "r") as open_file:
        lines = open_file.readlines()
    return _remove_trailing_newlines(lines)


def _remove_trailing_newlines(lines):
    lines_without_newlines = []
    for line in lines:
        lines_without_newlines.append(_remove_trailing_newline(line))
    return lines_without_newlines


def _remove_trailing_newline(line):
    return line.replace('\n', "").replace('\r', "")
