from erika.TicTacToe import *
import rpyc


class TicTacToePlayer(TicTacToe):

    def __init__(self, erika, name):
        self.name = name
        self.connection = rpyc.connect("localhost", 18861, keepalive=True)
        self.server = self.connection.root
        super().__init__(erika=erika)

    def _prepare_game(self):
        super()._prepare_game()
        self.turn = self.server.get_turn()

    def game_loop(self):
        while not self.game_over:
            if self.turn == Players.Erika.value:
                opponent_x, opponent_y = self.server.get_opponent_move()
                self.move_abs(opponent_x, opponent_y)
                self.make_move(Players.Erika)
                self.turn = Players.Player1.value
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
                self.server.set_last_move(self.last_move_x, self.last_move_y)

            self._check_winner_for_last_move()


if __name__ == "__main__":
    from erika.erika_mock import CharacterBasedErikaMock

    mock = CharacterBasedErikaMock()
    player = TicTacToePlayer(mock, "test")
    player.start_game()
