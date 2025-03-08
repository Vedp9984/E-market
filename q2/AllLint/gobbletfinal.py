#!/usr/bin/env python3
"""
Gobblet Game Implementation
A strategy board game where players place stackable pieces on a 4x4 grid.
"""
# Standard library imports
import sys

# Third-party imports
# pylint: disable=no-member
import pygame
# pylint: enable=no-member

from colors import BACKGROUND
from constants import WIDTH, HEIGHT, ROWS, COLS, CELL_SIZE, SIDE_BOX_WIDTH, SIDE_GRID_COLS
from UI.gameUI import GameUI
from UI.board import Board
from UI.piece import Piece
from player import Player
# Initialize pygame with error handling
try:
    # pylint: disable=no-member
    pygame.init()
    # pylint: enable=no-member
except pygame.error as e:
    print(f"Failed to initialize pygame: {e}")
    sys.exit(1)

class Game:
    """Main game class that handles game logic and state management."""
    def __init__(self):
        """Initialize game state and components."""
        self.board = Board()
        self.players = [Player(0), Player(1)]
        self.ui = GameUI()
        self.turn = 0
        self.game_over = False
        self.draw_game = False
        self.game_ending = False
        self.ending_message = ""
        self.player_response = [None, None]
        self.restart_timer = None
        self.end_timer = None
        self.tutorial_active = True
        self.ui.error_message = ""

    def reset(self):
        """Reset the game state to initial conditions."""
        self.board = Board()
        self.players = [Player(0), Player(1)]
        self.turn = 0
        self.game_over = False
        self.draw_game = False
        self.player_response = [None, None]
        self.ui.error_message = "Game started! Player 1's turn."

    def _handle_game_over_click(self, x_pos, y_pos):
        """Handle click events when game is over."""
        for player in [0, 1]:
            yes_button, no_button = self.ui.get_player_buttons(player)
            if (yes_button.collidepoint(x_pos, y_pos) and
                self.player_response[player] is None):
                self.player_response[player] = True
            elif (no_button.collidepoint(x_pos, y_pos) and
                  self.player_response[player] is None):
                self.player_response[player] = False

        if all(response is not None for response in self.player_response):
            if all(self.player_response):
                self.restart_timer = pygame.time.get_ticks() + 1500
            else:
                self._set_ending_state()

    def _set_ending_state(self):
        """Set the game ending state and message."""
        self.game_ending = True
        if not any(self.player_response):
            self.ending_message = "Both players decided to quit"
        elif not self.player_response[0]:
            self.ending_message = "Player 1 decided to quit"
        else:
            self.ending_message = "Player 2 decided to quit"
        self.end_timer = pygame.time.get_ticks() + 3000

    def handle_click(self, x_pos, y_pos):
        """
          Handle mouse click events.

          Args:
           x_pos: X-coordinate of click
           y_pos: Y-coordinate of click
         """
        if self.game_over and not self.game_ending:
            self._handle_game_over_click(x_pos, y_pos)
            return

        if self.game_over or self.game_ending:
            return

        self._check_side_box_clicks(x_pos, y_pos)
        self._check_board_clicks(x_pos, y_pos)

    def _check_side_box_clicks(self, x_pos, y_pos):
        """Check for clicks in the side boxes."""
        for player in [0, 1]:
            for i, (size, _) in enumerate(self.players[player].pieces):
                side_x = 0 if player == 0 else WIDTH - SIDE_BOX_WIDTH
                row, col = divmod(i, SIDE_GRID_COLS)
                center_x = side_x + SIDE_BOX_WIDTH // 2
                center_y = 100 + row * 100 + col * 50

                if (x_pos - center_x) ** 2 + (y_pos - center_y) ** 2 <= size ** 2:
                    self.ui.dragging_piece = (size, player, "side", i)
                    break

    def _check_board_clicks(self, x_pos, y_pos):
        """Check for clicks on the game board."""
        if (not self.ui.dragging_piece and
            SIDE_BOX_WIDTH <= x_pos <= WIDTH - SIDE_BOX_WIDTH):
            col = (x_pos - SIDE_BOX_WIDTH) // CELL_SIZE
            row = y_pos // CELL_SIZE
            if (0 <= row < ROWS and 0 <= col < COLS and
                self.board.grid[row][col]):
                size, player = self.board.grid[row][col][-1]
                center_x = SIDE_BOX_WIDTH + col * CELL_SIZE + CELL_SIZE // 2
                center_y = row * CELL_SIZE + CELL_SIZE // 2

                if ((x_pos - center_x) ** 2 +
                    (y_pos - center_y) ** 2 <= size ** 2):
                    self.ui.dragging_piece = (size, player, "board", (row, col))

    def handle_drop(self, x_pos, y_pos):
        """Handle piece drop events."""
        if not self.ui.dragging_piece:
            return False

        size, player, origin_type, origin_index = self.ui.dragging_piece

        if not self._validate_drop(player):
            return False

        if not self._is_valid_board_position(x_pos, y_pos):
            return False

        col = (x_pos - SIDE_BOX_WIDTH) // CELL_SIZE
        row = y_pos // CELL_SIZE

        return self._process_drop(size, player, origin_type, origin_index, row, col)

    def _validate_drop(self, player):
        """Validate if the drop is allowed based on game state."""
        if self.board.check_winner(player):
            self.game_over = True
            self.ui.error_message = f"Player {player + 1} wins! Play again?"
            return False
        if player != self.turn:
            self.ui.error_message = "Not your turn!"
            return False
        return True

    def _is_valid_board_position(self, x_pos, y_pos):
        """Check if the drop position is within the valid board area."""
        return (SIDE_BOX_WIDTH <= x_pos <= WIDTH - SIDE_BOX_WIDTH and
                0 <= y_pos <= HEIGHT)

    def _process_drop(self, size, player, origin_type, origin_index, row, col):
        """Process the piece drop on the board."""
        if not (0 <= row < ROWS and 0 <= col < COLS):
            self.ui.error_message = "Invalid position!"
            return False

        piece = Piece(size, player)
        if not self.board.is_valid_move(piece, row, col):
            if origin_type == "board":
                self.board.place_piece(piece, origin_index[0], origin_index[1])
            self.ui.error_message = "Invalid move: Cannot place on a larger piece!"
            return False

        self._execute_move(piece, player, origin_type, origin_index, row, col)
        return True

    def _execute_move(self, piece, player, origin_type, origin_index, row, col):
        """Execute the move and update game state."""
        if origin_type == "side":
            self.players[player].remove_piece(piece.size)
        elif origin_type == "board":
            self.board.remove_top_piece(origin_index[0], origin_index[1])

        self.board.place_piece(piece, row, col)
        self._check_game_state(player)
        self.turn = 1 - self.turn
        self.ui.error_message = ""

    def _check_game_state(self, player):
        """Check for win or draw conditions."""
        if self.board.check_winner(player):
            self.game_over = True
            self.ui.error_message = f"Player {player + 1} wins! Play again?"
        elif self.board.check_draw():
            self.game_over = True
            self.draw_game = True
            self.ui.error_message = "Game is a draw! Play again?"

    def update(self):
        """Update game state each frame."""
        if not self._update_hover():
            return False
        return self._check_timers()

    def _update_hover(self):
        """Update hover effect on the board."""
        mouse_x, mouse_y = pygame.mouse.get_pos()
        if (SIDE_BOX_WIDTH <= mouse_x <= WIDTH - SIDE_BOX_WIDTH and
            0 <= mouse_y <= HEIGHT and not self.game_over and
            not self.game_ending and not self.tutorial_active):
            col = (mouse_x - SIDE_BOX_WIDTH) // CELL_SIZE
            row = mouse_y // CELL_SIZE
            self.ui.hover_cell = (row, col) if 0 <= row < ROWS and 0 <= col < COLS else None
        else:
            self.ui.hover_cell = None
        return True

    def _check_timers(self):
        """Check and handle game timers."""
        if self.restart_timer and pygame.time.get_ticks() >= self.restart_timer:
            self.reset()
            self.restart_timer = None
        if self.end_timer and pygame.time.get_ticks() >= self.end_timer:
            return False
        return True

    def render(self):
        """Render the game state."""
        self.ui.screen.fill(BACKGROUND)
        if not self.tutorial_active:
            self._render_game()
        else:
            self.ui.show_tutorial()
        pygame.display.flip()

    def _render_game(self):
        """Render the main game elements."""
        self.board.render(self.ui.screen, self.ui.hover_cell)
        self.ui.draw_side_boxes(self.players, self.turn,
                              self.game_over, self.game_ending)
        self.ui.draw_dragging_piece()
        self.ui.display_message(self.game_ending)
        if self.game_over and not self.game_ending:
            self.ui.draw_game_over(self.draw_game, self.turn, self.player_response)
        if self.game_ending:
            self.ui.draw_game_ending(self.ending_message)

    def run(self):
        """Main game loop."""
        running = True
        while running:
            running = self._process_events() and running
            running = self.update() and running
            self.render()
            pygame.time.delay(20)
        pygame.quit()
        sys.exit()

    def _process_events(self):
        """Process game events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if self._handle_tutorial_exit(event):
                continue
            if self._handle_mouse_events(event):
                continue
        return True

    def _handle_tutorial_exit(self, event):
        """Handle tutorial exit conditions."""
        if self.tutorial_active and (event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN)):
            self.tutorial_active = False
            self.ui.error_message = "Game started! Player 1's turn."
            return True
        return False

    def _handle_mouse_events(self, event):
        """Handle mouse input events."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not self.tutorial_active:
            self.handle_click(event.pos[0], event.pos[1])
            return True
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if (self.ui.dragging_piece and not self.game_over and
                not self.game_ending and not self.tutorial_active):
                self.handle_drop(event.pos[0], event.pos[1])
                self.ui.dragging_piece = None
            return True
        return False

if __name__ == "__main__":
    game = Game()
    game.run()