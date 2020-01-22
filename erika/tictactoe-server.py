import rpyc
from erika.TicTacToe import *
from rpyc.utils.server import ThreadedServer
from erika.erika_mock import CharacterBasedErikaMock


class TicTacToeServer(rpyc.Service, TicTacToe):

    def __init__(self):
        mock = CharacterBasedErikaMock()
        super().__init__(erika=mock)

    def on_connect(self, conn):
        # code that runs when a connection is created
        # (to init the service, if needed)
        self.start_game()

    def on_disconnect(self, conn):
        # code that runs after the connection has already closed
        # (to finalize the service, if needed)
        pass

    def player_select(self, _):
        if self.board[self.pos_y][self.pos_x] == Players.N0NE.value:
            self.make_move(Players.Erika)
            self.turn = Players.Player1.value

    def exposed_get_opponent_move(self):
        self.turn = Players.Erika.value

        while self.turn == Players.Erika.value:
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
        return self.last_move_x, self.last_move_y

    def exposed_set_last_move(self, x, y):
        self.move_abs(x, y)
        self.make_move(Players.Player1)
        self._check_winner_for_last_move()

    def exposed_get_turn(self):
        return self.turn

    def game_loop(self):
        pass


if __name__ == "__main__":
    t = ThreadedServer(TicTacToeServer, port=18861)
    t.start()
    # TicTacToeServer()
