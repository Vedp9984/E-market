
import pygame
from colors import WHITE, GRID_COLOR, HIGHLIGHT_COLOR
from constants import COLS, ROWS, SIDE_BOX_WIDTH, WIDTH, HEIGHT, CELL_SIZE
from UI.piece import Piece

class Board:
    def __init__(self):
        self.grid = [[[] for _ in range(COLS)] for _ in range(ROWS)]
        self.grid = [[[] for _ in range(COLS)] for _ in range(ROWS)]

    def place_piece(self, piece, row, col):
        """Place a piece on the board."""
        self.grid[row][col].append((piece.size, piece.player))

    def remove_top_piece(self, row, col):
        """Remove the top piece from a cell."""
        if self.grid[row][col]:
            return self.grid[row][col].pop()
        return None

    def get_top_piece(self, row, col):
        """Get the top piece from a cell."""
        if self.grid[row][col]:
            return self.grid[row][col][-1]
        return None

    def is_valid_move(self, piece, row, col):
        """Check if a move is valid."""
        top_piece = self.get_top_piece(row, col)
        return not top_piece or top_piece[0] < piece.size

    def check_winner(self, player):
        """Check if a player has won."""
        # Check rows
        for row in range(ROWS):
            if all(self.grid[row][col] and self.grid[row][col][-1][1] == player for col in range(COLS)):
                return True

        # Check columns
        for col in range(COLS):
            if all(self.grid[row][col] and self.grid[row][col][-1][1] == player for row in range(ROWS)):
                return True

        # Check diagonals
        if all(self.grid[i][i] and self.grid[i][i][-1][1] == player for i in range(ROWS)):
            return True
        if all(self.grid[i][ROWS - 1 - i] and self.grid[i][ROWS - 1 - i][-1][1] == player for i in range(ROWS)):
            return True

        return False

    def check_draw(self):
        """Check if the game is a draw."""
        return all(self.grid[row][col] for row in range(ROWS) for col in range(COLS))

    def render(self, screen, hover_cell=None):
        """Render the board."""
        # Draw the board background
        board_rect = pygame.Rect(SIDE_BOX_WIDTH, 0, WIDTH - 2 * SIDE_BOX_WIDTH, HEIGHT)
        pygame.draw.rect(screen, WHITE, board_rect)
        pygame.draw.rect(screen, GRID_COLOR, board_rect, 3)

        # Draw grid lines with shadows
        for row in range(1, ROWS):
            y = row * CELL_SIZE
            # Shadow
            pygame.draw.line(screen, (200, 200, 200), (SIDE_BOX_WIDTH + 3, y + 3),
                             (WIDTH - SIDE_BOX_WIDTH + 3, y + 3), 5)
            # Main line
            pygame.draw.line(screen, GRID_COLOR, (SIDE_BOX_WIDTH, y),
                             (WIDTH - SIDE_BOX_WIDTH, y), 5)

        for col in range(1, COLS):
            x = SIDE_BOX_WIDTH + col * CELL_SIZE
            # Shadow
            pygame.draw.line(screen, (200, 200, 200), (x + 3, 3),
                             (x + 3, HEIGHT + 3), 5)
            # Main line
            pygame.draw.line(screen, GRID_COLOR, (x, 0),
                             (x, HEIGHT), 5)

        # Highlight hovered cell
        if hover_cell:
            row, col = hover_cell
            x = SIDE_BOX_WIDTH + col * CELL_SIZE
            y = row * CELL_SIZE
            highlight_rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
            highlight_surface = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
            highlight_surface.fill(HIGHLIGHT_COLOR)
            screen.blit(highlight_surface, highlight_rect)

        # Draw pieces on board
        for row in range(ROWS):
            for col in range(COLS):
                if self.grid[row][col]:
                    size, player = self.grid[row][col][-1]
                    x = SIDE_BOX_WIDTH + col * CELL_SIZE + CELL_SIZE // 2
                    y = row * CELL_SIZE + CELL_SIZE // 2
                    piece = Piece(size, player)
                    piece.render(screen, x, y)