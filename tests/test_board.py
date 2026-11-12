"""Tests for tic_tac_toe.board.

These check the Board class on its own: placing marks, rejecting bad moves,
and detecting wins, draws and games still in progress. Run them with
`uv run pytest`.
"""

import pytest

from tic_tac_toe.board import (
    WINNING_LINES,
    Board,
    CellOccupiedError,
    CellOutOfRangeError,
    InvalidMarkError,
    InvalidMoveError,
)


def make_board(layout: str) -> Board:
    """Build a Board from a 9-character string, to keep tests readable.

    Args:
        layout: Nine characters, one per cell in order 1-9. Use "X", "O",
            or "." for an empty cell.

    Returns:
        A Board with those marks placed.

    Example:
        >>> make_board("XO.......").get(2)
        'O'
    """
    board = Board()
    for cell_number, char in enumerate(layout, start=1):
        # "." means leave the cell empty.
        if char != ".":
            board.place(cell_number, char)
    return board


# --- Starting state --------------------------------------------------------


def test_new_board_is_empty() -> None:
    """A fresh board has all 9 cells free, no winner and no draw."""
    board = Board()
    assert board.empty_cells() == [1, 2, 3, 4, 5, 6, 7, 8, 9]
    assert board.winner() is None
    assert board.is_draw() is False


# --- Placing marks ---------------------------------------------------------


def test_place_puts_mark_in_cell() -> None:
    """After placing, the cell holds the mark and is no longer empty."""
    board = Board()
    board.place(5, "X")
    assert board.get(5) == "X"
    assert 5 not in board.empty_cells()


# parametrize runs this test once for each value in the list, and each run
# is reported separately, so you can see exactly which input failed.
@pytest.mark.parametrize("cell", [0, 10, -1, 100])
def test_place_out_of_range_raises(cell: int) -> None:
    """Cell numbers outside 1-9 are rejected with CellOutOfRangeError."""
    board = Board()
    # pytest.raises passes only if the code inside the `with` block raises
    # that exception. `match` also checks the error message (a regex).
    with pytest.raises(CellOutOfRangeError, match="between 1 and 9"):
        board.place(cell, "X")


@pytest.mark.parametrize("cell", ["5", 5.0, True, None])
def test_place_non_integer_cell_raises(cell: object) -> None:
    """Values that aren't plain ints (including True) are rejected."""
    board = Board()
    with pytest.raises(CellOutOfRangeError, match="whole number"):
        board.place(cell, "X")  # type: ignore[arg-type]


def test_place_on_taken_cell_raises() -> None:
    """Playing in a filled cell raises CellOccupiedError and keeps the old mark."""
    board = Board()
    board.place(3, "X")
    with pytest.raises(CellOccupiedError, match="Cell 3 is already taken by X"):
        board.place(3, "O")
    # The failed move must not have changed the board.
    assert board.get(3) == "X"


def test_both_move_errors_share_a_base_class() -> None:
    """The CLI can catch InvalidMoveError to handle either kind of bad move."""
    assert issubclass(CellOutOfRangeError, InvalidMoveError)
    assert issubclass(CellOccupiedError, InvalidMoveError)


@pytest.mark.parametrize("mark", ["x", "Z", "", "XO"])
def test_place_invalid_mark_raises(mark: str) -> None:
    """Only "X" and "O" are accepted as marks."""
    board = Board()
    with pytest.raises(InvalidMarkError):
        board.place(1, mark)  # type: ignore[arg-type]


def test_get_out_of_range_raises() -> None:
    """get() checks the cell range the same way place() does."""
    with pytest.raises(CellOutOfRangeError):
        Board().get(0)


# --- Winning ---------------------------------------------------------------


def test_there_are_exactly_eight_winning_lines() -> None:
    """3 rows + 3 columns + 2 diagonals = 8, with no duplicates."""
    assert len(set(WINNING_LINES)) == 8


# Stacking two parametrize decorators runs every combination: 8 lines x 2
# marks = 16 test cases. `ids` gives each line a readable name in the output.
@pytest.mark.parametrize(
    "line",
    [
        (1, 2, 3),
        (4, 5, 6),
        (7, 8, 9),
        (1, 4, 7),
        (2, 5, 8),
        (3, 6, 9),
        (1, 5, 9),
        (3, 5, 7),
    ],
    ids=[
        "top-row",
        "middle-row",
        "bottom-row",
        "left-col",
        "middle-col",
        "right-col",
        "diag-down",
        "diag-up",
    ],
)
@pytest.mark.parametrize("mark", ["X", "O"])
def test_winner_detects_every_line(line: tuple[int, int, int], mark: str) -> None:
    """Three of the same mark on any winning line is a win for that mark."""
    board = Board()
    for cell in line:
        board.place(cell, mark)  # type: ignore[arg-type]
    assert board.winner() == mark
    # A won board is never a draw.
    assert board.is_draw() is False


def test_mixed_line_is_not_a_win() -> None:
    """A full row with different marks doesn't count."""
    board = make_board("XOX......")
    assert board.winner() is None


def test_win_on_full_board_is_not_a_draw() -> None:
    """If the last move fills the board AND completes a line, it's a win."""
    # X O X
    # O X O
    # O X X   <- X wins on the 1-5-9 diagonal
    board = make_board("XOXOXOOXX")
    assert board.empty_cells() == []
    assert board.winner() == "X"
    assert board.is_draw() is False


# --- Draws and games in progress -------------------------------------------


def test_draw() -> None:
    """A full board with no three-in-a-row is a draw."""
    # X O X
    # X O O
    # O X X
    board = make_board("XOXXOOOXX")
    assert board.empty_cells() == []
    assert board.winner() is None
    assert board.is_draw() is True


def test_game_in_progress() -> None:
    """Part-way through a game: no winner, no draw, some cells free."""
    # X . O
    # . X .
    # . . O
    board = make_board("X.O.X...O")
    assert board.winner() is None
    assert board.is_draw() is False
    assert board.empty_cells() == [2, 4, 6, 7, 8]
