"""The tic-tac-toe board: a 3x3 grid and the rules about what is on it.

This module knows *only* about the grid itself: which cells are filled, whether
a move is legal, and whether someone has won or the game is a draw. It knows
nothing about whose turn it is (that is game.py's job) or how to show the
board to a person (that is cli.py's job). Keeping it this small makes it easy
to test, and it never calls print() or input().

Cells are numbered 1-9, left to right, top to bottom:

     1 | 2 | 3
    ---+---+---
     4 | 5 | 6
    ---+---+---
     7 | 8 | 9
"""

from typing import Literal

# A "type alias": a short name for a longer type. `Literal["X", "O"]` means
# "a str, but only the exact value 'X' or 'O'". Type checkers and editors use
# this to warn you if you write board.place(5, "Z"). Python itself does NOT
# enforce it at runtime, which is why place() also checks the mark by hand.
Mark = Literal["X", "O"]

# The valid marks, for the runtime check in place().
VALID_MARKS: tuple[str, ...] = ("X", "O")

# All 8 ways to get three in a row, written with the 1-9 cell numbers players
# see. Listing them out explicitly is clearer than computing them with loops,
# and there are only eight.
WINNING_LINES: tuple[tuple[int, int, int], ...] = (
    # Rows
    (1, 2, 3),
    (4, 5, 6),
    (7, 8, 9),
    # Columns
    (1, 4, 7),
    (2, 5, 8),
    (3, 6, 9),
    # Diagonals
    (1, 5, 9),
    (3, 5, 7),
)


class InvalidMoveError(ValueError):
    """Base class for every "you can't play there" error.

    The CLI can catch this one class and handle both kinds of bad move at
    once, while the tests can still check for the exact subclass.
    """


class CellOutOfRangeError(InvalidMoveError):
    """Raised when a cell number is not between 1 and 9."""


class CellOccupiedError(InvalidMoveError):
    """Raised when a player tries to play in a cell that already has a mark."""


class InvalidMarkError(ValueError):
    """Raised when the mark is not "X" or "O".

    This means the code has a bug, not that the player made a bad move. That
    is why it is not a subclass of InvalidMoveError.
    """


class Board:
    """A 3x3 tic-tac-toe grid.

    Internally the cells are stored in a list of 9 items (index 0-8), where
    each item is None for an empty cell or "X"/"O" for a filled one. Callers
    always use the human-friendly numbers 1-9; the conversion to list indexes
    happens only inside this class.

    Example:
        >>> board = Board()
        >>> board.place(5, "X")
        >>> board.get(5)
        'X'
        >>> 5 in board.empty_cells()
        False
    """

    def __init__(self) -> None:
        """Create an empty board with all 9 cells free."""
        # `Mark | None` means "either a Mark or None". [None] * 9 makes a
        # list of nine Nones, so the board starts empty.
        self._cells: list[Mark | None] = [None] * 9

    def _index(self, cell: int) -> int:
        """Turn a 1-9 cell number into a 0-8 list index, checking the range.

        The leading underscore is a Python convention meaning "internal
        helper; code outside this class shouldn't call it".

        Args:
            cell: A cell number, expected to be 1-9.

        Returns:
            The matching list index, 0-8.

        Raises:
            CellOutOfRangeError: If `cell` is not an int between 1 and 9.
        """
        # bool is a subclass of int in Python (True == 1), so reject it
        # explicitly; otherwise place(True, "X") would quietly mean cell 1.
        if isinstance(cell, bool) or not isinstance(cell, int):
            raise CellOutOfRangeError(
                f"Cell must be a whole number from 1 to 9, got {cell!r}."
            )
        if not 1 <= cell <= 9:
            raise CellOutOfRangeError(f"Cell must be between 1 and 9, got {cell}.")
        # Players count from 1 but lists count from 0.
        return cell - 1

    def get(self, cell: int) -> Mark | None:
        """Return what is in a cell.

        Args:
            cell: The cell number, 1-9.

        Returns:
            "X" or "O" if the cell is filled, or None if it is empty.

        Raises:
            CellOutOfRangeError: If `cell` is not between 1 and 9.

        Example:
            >>> Board().get(1) is None
            True
        """
        return self._cells[self._index(cell)]

    def place(self, cell: int, mark: Mark) -> None:
        """Put a mark in an empty cell.

        Args:
            cell: The cell number, 1-9.
            mark: "X" or "O".

        Raises:
            InvalidMarkError: If `mark` is not "X" or "O".
            CellOutOfRangeError: If `cell` is not between 1 and 9.
            CellOccupiedError: If the cell already holds a mark.

        Example:
            >>> board = Board()
            >>> board.place(1, "X")
            >>> board.place(1, "O")
            Traceback (most recent call last):
            ...
            tic_tac_toe.board.CellOccupiedError: Cell 1 is already taken by X.
        """
        # Check the mark first. The type hint alone won't stop a wrong value
        # at runtime, and a bad mark would break the winner logic.
        if mark not in VALID_MARKS:
            raise InvalidMarkError(f'Mark must be "X" or "O", got {mark!r}.')

        # Convert to a list index; this also rejects out-of-range cells.
        index = self._index(cell)

        # Refuse to overwrite an existing mark, and say who is already there
        # so the error message is useful to the player.
        current = self._cells[index]
        if current is not None:
            raise CellOccupiedError(f"Cell {cell} is already taken by {current}.")

        self._cells[index] = mark

    def empty_cells(self) -> list[int]:
        """List the cell numbers that are still free.

        Returns:
            The empty cell numbers (1-9) in ascending order. An empty list
            means the board is full.

        Example:
            >>> board = Board()
            >>> board.place(2, "O")
            >>> board.empty_cells()
            [1, 3, 4, 5, 6, 7, 8, 9]
        """
        empty: list[int] = []
        # enumerate(..., start=1) gives (1, item0), (2, item1), ... so we get
        # the player-facing cell numbers directly.
        for cell_number, value in enumerate(self._cells, start=1):
            if value is None:
                empty.append(cell_number)
        return empty

    def winner(self) -> Mark | None:
        """Find out who, if anyone, has three in a row.

        Returns:
            "X" or "O" if that player has completed a row, column or
            diagonal; otherwise None.

        Example:
            >>> board = Board()
            >>> for cell in (1, 5, 9):
            ...     board.place(cell, "X")
            >>> board.winner()
            'X'
        """
        # Check each of the 8 possible lines.
        for a, b, c in WINNING_LINES:
            first = self.get(a)
            # An empty line can't be a win. Without this check, three empty
            # cells (None, None, None) would count as "all the same".
            if first is None:
                continue
            if first == self.get(b) == self.get(c):
                return first
        # No line is complete.
        return None

    def is_full(self) -> bool:
        """Return True if every cell has a mark in it."""
        return len(self.empty_cells()) == 0

    def is_draw(self) -> bool:
        """Return True if the board is full and nobody has won.

        A full board can still contain a win (the last move might complete
        a line), so both conditions are needed.

        Returns:
            True for a draw, False if the game is won or still in progress.
        """
        return self.is_full() and self.winner() is None
