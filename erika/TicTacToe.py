from enum import Enum

import numpy as np


class Players(Enum):
    Erika = 1
    Player1 = 2
    N0NE = 0

    player_chars = [" ", "o", "x"]

    @property
    def char(self):
        return self.player_chars.value[self.value]


def create_field(field_size=3, cell_width=3, cell_height=1, vertical_sep="#", horizontal_sep="#", x_offset=0):
    result = []
    cell = " " * cell_width
    padding = " " * x_offset
    row = padding + vertical_sep.join([cell] * field_size)
    horizontal_line = padding + (horizontal_sep * (len(row) - x_offset))

    for i in range(0, field_size - 1):
        result.extend([row] * cell_height)
        result.append(horizontal_line)

    result.extend([row] * cell_height)
    return result


class TicTacToe:

    def __init__(self, erika):
        # configure game field
        self.field_size = 3
        self.cell_width = 3
        self.cell_height = 1
        self.vertical_sep = "|"
        self.horizontal_sep = "-"
        assert self.field_size % 2 == 1
        self.board = np.zeros((self.field_size, self.field_size), dtype=np.uint8)

        # setup initial cursor position
        self.pos_y = self.pos_x = 0
        self.last_move_x = self.pos_x
        self.last_move_y = self.pos_y

        self.game_over = False
        self.turn = -1

        # setup erika
        self.erika = erika

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.erika.__exit__()

    def start_game(self):
        # disable keyboard echo
        self.erika.set_keyboard_echo(False)

        self.erika.print_ascii("\n")

        self._print_initial_field()

        self._cursor_to_start_position()

        self.turn = np.random.randint(1, 3)
        self.game_over = False
        self.game_loop()

    def _print_initial_field(self):

        x_offset = 30
        ascii_field = create_field(self.field_size, cell_height=self.cell_height
                                   , cell_width=self.cell_width, vertical_sep=self.vertical_sep
                                   , horizontal_sep=self.horizontal_sep, x_offset=x_offset)

        self.erika.print_ascii("\n".join(ascii_field))

        for i in range(len(ascii_field[0]) - x_offset):
            self.erika.move_left()
        for i in range(len(ascii_field) - 1):
            self.erika.move_up()

    def _cursor_to_start_position(self):
        # move to center of block
        for i in range(self.field_size // 2):
            self.erika.move_right()

        # move to initial position (middle)
        self.move_abs(self.field_size // 2, self.field_size // 2)

    def game_loop(self):
        while not self.game_over:
            if self.turn == Players.Erika.value:
                self.ai_select()
            else:
                inp = self.erika.read()
                input_mapping = {
                    "w": self.move_up
                    , "a": self.move_left
                    , "s": self.move_down
                    , "d": self.move_right
                    , " ": self.player_select
                    , "\n": self.player_select
                }
                input_mapping.get(inp, lambda _: "")(1)

            self._check_winner_for_last_move()

    @staticmethod
    def check_row(game_field, last):
        return (last == game_field).all()

    def _check_winner_for_last_move(self):
        if self.game_over:
            return

        last = self.board[self.last_move_y, self.last_move_x]

        if last == Players.N0NE.value:
            return

        if self.check_row(self.board[self.last_move_y], last):
            self._won(last)
        elif self.check_row(self.board.T[self.last_move_x], last):
            self._won(last)
        elif self.check_row(np.diag(self.board), last):
            self._won(last)
        elif self.check_row(np.diag(np.fliplr(self.board)), last):
            self._won(last)
        else:
            next_move_candidates = np.argwhere(self.board == Players.N0NE.value)
            # no more move options
            if not len(next_move_candidates):
                self._tie()
                return

    def _tie(self):
        self.game_over = True
        self.move_abs(0, self.field_size - 1)
        self.erika._cursor_back(1)
        self.erika._cursor_down(1)
        self.erika.print_ascii("Tie!\n")
        self.erika.print_ascii("Press any key to exit.\n")
        self.erika.read()

    def _won(self, winner):
        self.game_over = True
        self.move_abs(0, self.field_size - 1)
        self.erika._cursor_back(1)
        self.erika._cursor_down(1)
        self.erika.print_ascii(f"{Players(winner).name} won.\n")
        self.erika.print_ascii("Press any key to exit.\n")
        self.erika.read()

    def move_abs(self, x, y):
        if self.pos_y < y:
            self.move_down(y - self.pos_y)
        elif self.pos_y > y:
            self.move_up(self.pos_y - y)

        if self.pos_x < x:
            self.move_right(x - self.pos_x)
        elif self.pos_x > x:
            self.move_left(self.pos_x - x)

    def move_up(self, n):
        if self.pos_y - n >= 0:
            self.pos_y -= n
            steps_to_move = (self.cell_height + len(self.horizontal_sep)) * n
            for i in range(steps_to_move):
                self.erika.move_up()

    def move_down(self, n):
        if self.pos_y + n < self.field_size:
            self.pos_y += n
            steps_to_move = (self.cell_height + len(self.horizontal_sep)) * n
            for i in range(steps_to_move):
                self.erika.move_down()

    def move_left(self, n):
        if self.pos_x - n >= 0:
            self.pos_x -= n
            steps_to_move = (self.cell_width + len(self.vertical_sep)) * n
            for i in range(steps_to_move):
                self.erika.move_left()

    def move_right(self, n):
        if self.pos_x + n < self.field_size:
            self.pos_x += n
            steps_to_move = (self.cell_width + len(self.vertical_sep)) * n
            for i in range(steps_to_move):
                self.erika.move_right()

    def update_last_move(self):
        self.last_move_x = self.pos_x
        self.last_move_y = self.pos_y

    def player_select(self, _):
        if self.board[self.pos_y][self.pos_x] == Players.N0NE.value:
            self.make_move(Players.Player1)
            self.turn = Players.Erika.value

    def min_max(self, board, player, last_move=None):
        candidates = np.argwhere(board == Players.N0NE.value)
        # erikas_choice = candidates[np.random.choice(candidates.shape[0])]
        best_score = -2
        best_move = None
        for move in candidates:
            board_cp = board.copy()
            board_cp[move[0], move[1]] = player.value
            if self._check_winner_for_min_max(board_cp, move):
                return 1, best_move
            score = -self.min_max(board_cp, Players.Erika if player == Players.Player1 else Players.Player1, move)[0]
            if score > best_score:
                best_move = move
                best_score = score
        if best_move is None:
            return 0, best_move

        return 1, best_move

    def _check_winner_for_min_max(self, board, last_move):
        player = board[last_move[0], last_move[1]]

        if self.check_row(board[last_move[0]], player):
            return True
        elif self.check_row(board.T[last_move[1]], player):
            return True
        elif self.check_row(np.diag(board), player):
            return True
        elif self.check_row(np.diag(np.fliplr(board)), player):
            return True

        return False

    def make_move(self, player):
        self.board[self.pos_y, self.pos_x] = player.value
        self.erika.print_ascii(player.char)
        self.erika.move_left()
        self.update_last_move()

    def ai_select(self):
        # TODO: implement different strategies
        candidates = np.argwhere(self.board == Players.N0NE.value)
        erikas_choice = candidates[np.random.choice(candidates.shape[0])]
        # erikas_choice = self.min_max(self.board, Players.Erika)[1]

        self.move_abs(erikas_choice[1], erikas_choice[0])
        self.make_move(Players.Erika)
        self.turn = Players.Player1.value


if __name__ == "__main__":
    from erika.erika_mock import CharacterBasedErikaMock

    erika = CharacterBasedErikaMock()
    with TicTacToe(erika) as game:
        game.start_game()
