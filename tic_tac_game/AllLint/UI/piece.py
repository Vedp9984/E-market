"""
Piece module for Gobblet Jr.
Defines the Piece class used in the game.
"""

# Standard library imports

# Third-party imports
# pylint: disable=no-member
import pygame
# pylint: enable=no-member

# Local imports
from colors import PLAYER_COLORS

class Piece:
    """Represents a game piece in Gobblet Jr."""

    SHADOW_COLOR = (100, 100, 100)
    HIGHLIGHT_COLOR = (255, 255, 255, 100)
    HIGHLIGHT_OFFSET = 4
    HIGHLIGHT_WIDTH = 2

    def __init__(self, size: int, player: int):
        """
        Initialize a game piece.

        Args:
            size: Size of the piece
            player: Player index (0 or 1)
        """
        self.size = size
        self.player = player

    def render(self, screen: pygame.Surface, x: int, y: int) -> None:
        """
        Render the piece on the screen.

        Args:
            screen: Pygame screen surface to draw on
            x: X-coordinate of the piece center
            y: Y-coordinate of the piece center
        """
        # Draw shadow
        pygame.draw.circle(screen, self.SHADOW_COLOR, (x + 3, y + 3), self.size)

        # Draw main circle
        pygame.draw.circle(screen, PLAYER_COLORS[self.player], (x, y), self.size)

        # Draw highlight
        highlight_radius = max(self.size - 5, int(self.size * 0.8))
        highlight_pos = (x - self.size // self.HIGHLIGHT_OFFSET, y - self.size // self.HIGHLIGHT_OFFSET)
        pygame.draw.circle(screen, self.HIGHLIGHT_COLOR, highlight_pos, highlight_radius // 2, self.HIGHLIGHT_WIDTH)