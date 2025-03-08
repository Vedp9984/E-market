"""
This module defines the Player class for the Gobblet game.
"""

from constants import PIECE_SIZES, SIDE_GRID_COLS, SIDE_BOX_WIDTH
from UI.piece import Piece

class Player:
    """
    Represents a player in the Gobblet game.
    """

    def __init__(self, player_id):
        """
        Initialize the player with an ID and pieces.

        :param player_id: The ID of the player.
        """
        self.player_id = player_id
        self.pieces = [(size, player_id) for size in PIECE_SIZES for _ in range(2)]

    def remove_piece(self, size):
        """
        Remove a piece of a given size from the player's pieces.

        :param size: The size of the piece to remove.
        """
        self.pieces.remove((size, self.player_id))

    def has_piece_size(self, size):
        """
        Check if the player has a piece of a given size.

        :param size: The size of the piece to check.
        :return: True if the player has the piece, False otherwise.
        """
        return (size, self.player_id) in self.pieces

    def render(self, screen, side_x):
        """
        Render the player's pieces on the screen.

        :param screen: The screen to render the pieces on.
        :param side_x: The x-coordinate for rendering.
        """
        for index, (size, _) in enumerate(self.pieces):
            row, col = divmod(index, SIDE_GRID_COLS)
            x = side_x + SIDE_BOX_WIDTH // 2
            y = 100 + row * 100 + col * 50
            piece = Piece(size, self.player_id)
            piece.render(screen, x, y)

# Ensure there is a final newline