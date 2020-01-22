import unittest

from erika.TicTacToe import Players
from erika.TicTacToe import TicTacToe
from erika.erika_mock import CharacterBasedErikaMock
from tests.erika_mock_unittest import assert_print_output

import pytest
from pytest_mock import mocker


# pytest-based tests must be functions on top level
def test_check_winner_beginning(mocker):
    with CharacterBasedErikaMock(11, 11, False, inside_unit_test=True) as my_erika:
        game = TicTacToe(my_erika)
        game._print_initial_field()
        game._cursor_to_start_position()
        mocker.patch.object(game, '_won')
        mocker.patch.object(game, '_tie')

        game._check_winner_for_last_move()

        assert not game._tie.called
        assert not game._won.called


def test_check_winner_win_erika(mocker):
    with CharacterBasedErikaMock(11, 11, False, inside_unit_test=True) as my_erika:
        game = TicTacToe(my_erika)
        game._print_initial_field()
        game._cursor_to_start_position()
        mocker.patch.object(game, '_won')
        mocker.patch.object(game, '_tie')
        game.board[0][1] = Players.Player1.value
        game.board[1][2] = Players.Player1.value
        game.board[2][0] = Players.Player1.value
        game.board[0][0] = Players.Erika.value
        game.board[1][1] = Players.Erika.value
        game.board[2][2] = Players.Erika.value

        game._check_winner_for_last_move()

        assert not game._tie.called
        assert game._won.called
        game._won.assert_called_with(Players.Erika.value)


def test_check_winner_win_player(mocker):
    with CharacterBasedErikaMock(11, 11, False, inside_unit_test=True) as my_erika:
        game = TicTacToe(my_erika)
        game._print_initial_field()
        game._cursor_to_start_position()
        mocker.patch.object(game, '_won')
        mocker.patch.object(game, '_tie')
        game.board[0][2] = Players.Player1.value
        game.board[1][2] = Players.Player1.value
        game.board[2][2] = Players.Player1.value
        game.board[2][0] = Players.Erika.value
        game.board[0][0] = Players.Erika.value
        game.board[1][1] = Players.Erika.value

        game.last_move_y = game.last_move_x = 1
        game._check_winner_for_last_move()
        assert not game._tie.called
        assert not game._won.called

        game.last_move_y = game.last_move_x = 2
        game._check_winner_for_last_move()
        assert not game._tie.called
        assert game._won.called
        game._won.assert_called_with(Players.Player1.value)


def test_check_winner_game_tied(mocker):
    with CharacterBasedErikaMock(11, 11, False, inside_unit_test=True) as my_erika:
        game = TicTacToe(my_erika)
        game._print_initial_field()
        game._cursor_to_start_position()
        mocker.patch.object(game, '_won')
        mocker.patch.object(game, '_tie')

        # o o x
        # x x o
        # o x x
        game.board[0][0] = Players.Erika.value
        game.board[0][1] = Players.Erika.value
        game.board[0][2] = Players.Player1.value

        game.board[1][0] = Players.Player1.value
        game.board[1][1] = Players.Player1.value
        game.board[1][2] = Players.Erika.value

        game.board[2][0] = Players.Erika.value
        game.board[2][1] = Players.Player1.value
        game.board[2][2] = Players.Player1.value

        game._check_winner_for_last_move()

        assert game._tie.called
        assert not game._won.called


# unittest-based tests must reside class inheriting from unittest
class TicTacToeUnitTest(unittest.TestCase):
    def test_initial_playing_field(self):
        """Simple test that the initial playing field looks like a tic tac toe grid"""
        with CharacterBasedErikaMock(11, 11, False, inside_unit_test=True) as my_erika:
            game = TicTacToe(my_erika)
            game._print_initial_field()
            assert_print_output(self, my_erika, ["   |   |   ",
                                                 "-----------",
                                                 "   |   |   ",
                                                 "-----------",
                                                 "   |   |   "])

    def test_erika_will_make_a_move(self):
        """test that Erika moves (puts an "o")"""
        with CharacterBasedErikaMock(11, 11, False, inside_unit_test=True) as my_erika:
            game = TicTacToe(my_erika)
            game._print_initial_field()
            game._cursor_to_start_position()

            any_x_on_field = any(['x' in line for line in my_erika.canvas])
            any_o_on_field = any(['o' in line for line in my_erika.canvas])
            self.assertFalse(any_x_on_field, "player should not have moved yet")
            self.assertFalse(any_o_on_field, "erika should not have moved yet")

            game.ai_select()

            any_x_on_field = any(['x' in line for line in my_erika.canvas])
            any_o_on_field = any(['o' in line for line in my_erika.canvas])
            self.assertFalse(any_x_on_field, "player should not have moved yet")
            self.assertTrue(any_o_on_field, "erika should have moved")
