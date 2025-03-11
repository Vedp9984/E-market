
"""
Game UI module for Gobblet Jr.
Handles the visual representation and interaction elements of the game.
"""
# Standard library imports
from typing import Optional, Tuple, List

# Third-party imports
# pylint: disable=no-member
import pygame
# pylint: enable=no-member
# Local imports
from colors import (
    PLAYER_COLORS, WHITE, GRID_COLOR, SIDE_BOX_COLORS,
    YES_COLOR, NO_COLOR, BUTTON_TEXT_COLOR
)
from constants import WIDTH, HEIGHT, SIDE_BOX_WIDTH
from UI.piece import Piece
class GameUI:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Gobblet Jr.")
        icon = pygame.Surface((32, 32), pygame.SRCALPHA)
        pygame.draw.circle(icon, PLAYER_COLORS[0], (16, 16), 12)
        pygame.draw.circle(icon, PLAYER_COLORS[1], (16, 16), 8)
        pygame.display.set_icon(icon)

        # Load fonts
        try:
            self.title_font = pygame.font.Font(None, 48)
            self.message_font = pygame.font.Font(None, 36)
            self.button_font = pygame.font.Font(None, 30)
        except:
            self.title_font = pygame.font.SysFont('Arial', 48)
            self.message_font = pygame.font.SysFont('Arial', 36)
            self.button_font = pygame.font.SysFont('Arial', 30)

        self.error_message = ""
        self.dragging_piece = None
        self.hover_cell = None

    def draw_side_boxes(self, players, current_turn, game_over=False, game_ending=False):
        player_names = ["Player 1 (Blue)", "Player 2 (Green)"]

        # Left box (Player 0)
        pygame.draw.rect(self.screen, SIDE_BOX_COLORS[0], (0, 0, SIDE_BOX_WIDTH, HEIGHT))
        pygame.draw.rect(self.screen, PLAYER_COLORS[0], (0, 0, SIDE_BOX_WIDTH, 40))
        p1_text = self.button_font.render(player_names[0], True, WHITE)
        self.screen.blit(p1_text, (SIDE_BOX_WIDTH//2 - p1_text.get_width()//2, 10))

        # Right box (Player 1)
        pygame.draw.rect(self.screen, SIDE_BOX_COLORS[1], (WIDTH - SIDE_BOX_WIDTH, 0, SIDE_BOX_WIDTH, HEIGHT))
        pygame.draw.rect(self.screen, PLAYER_COLORS[1], (WIDTH - SIDE_BOX_WIDTH, 0, SIDE_BOX_WIDTH, 40))
        p2_text = self.button_font.render(player_names[1], True, WHITE)
        self.screen.blit(p2_text, (WIDTH - SIDE_BOX_WIDTH//2 - p2_text.get_width()//2, 10))

        # Draw whose turn indicator
        if not game_over and not game_ending:
            turn_text = self.message_font.render("→ YOUR TURN", True, GRID_COLOR)
            if current_turn == 0:
                self.screen.blit(turn_text, (5, 45))
            else:
                self.screen.blit(turn_text, (WIDTH - SIDE_BOX_WIDTH + 5, 45))

        # Draw player's available pieces
        players[0].render(self.screen, 0)
        players[1].render(self.screen, WIDTH - SIDE_BOX_WIDTH)

    def draw_dragging_piece(self):
        if self.dragging_piece:
            x, y = pygame.mouse.get_pos()
            size, player, _, _ = self.dragging_piece
            piece = Piece(size, player)
            piece.render(self.screen, x, y)

    def display_message(self, game_ending=False):
        if self.error_message and not game_ending:
            text = self.message_font.render(self.error_message, True, (200, 30, 30))
            text_bg = pygame.Rect(WIDTH // 2 - text.get_width() // 2 - 10, HEIGHT - 60,
                                text.get_width() + 20, text.get_height() + 10)
            pygame.draw.rect(self.screen, (255, 240, 240), text_bg)
            pygame.draw.rect(self.screen, (200, 30, 30), text_bg, 2)
            self.screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT - 55))

    def draw_game_over(self, draw_game, turn, player_response):
        # Draw semi-transparent overlay
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        self.screen.blit(overlay, (0, 0))

        # Draw game over message
        if draw_game:
            text = self.title_font.render("GAME DRAW!", True, (255, 215, 0))
        else:
            winner = "Player 1" if turn == 0 else "Player 2"
            text = self.title_font.render(f"{winner} WINS!", True, (255, 215, 0))

        self.screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 3 - 50))

        # Draw play again question
        play_again_text = self.message_font.render("Would you like to play again?", True, (255, 255, 255))
        self.screen.blit(play_again_text, (WIDTH // 2 - play_again_text.get_width() // 2, HEIGHT // 3))

        # Draw Yes/No buttons for each player
        for player in [0, 1]:
            player_text = self.button_font.render(f"Player {player + 1}", True, WHITE)
            self.screen.blit(player_text, (WIDTH // 4 if player == 0 else 3 * WIDTH // 4 - player_text.get_width(),
                                        HEIGHT // 2 - 30))

            # Draw player response status
            if player_response[player] is None:
                status_text = self.button_font.render("Waiting for response...", True, (200, 200, 200))
                self.screen.blit(status_text, (WIDTH // 4 if player == 0 else 3 * WIDTH // 4 - status_text.get_width(),
                                            HEIGHT // 2))
            else:
                response_text = "YES" if player_response[player] else "NO"
                color = YES_COLOR if player_response[player] else NO_COLOR
                status_text = self.button_font.render(f"Response: {response_text}", True, color)
                self.screen.blit(status_text, (WIDTH // 4 if player == 0 else 3 * WIDTH // 4 - status_text.get_width(),
                                            HEIGHT // 2))

            # Yes button
            yes_button_width = 80
            yes_button_height = 40
            yes_button_x = WIDTH // 4 - yes_button_width // 2 if player == 0 else 3 * WIDTH // 4 - yes_button_width - 10
            yes_button_y = HEIGHT // 2 + 40

            yes_button_rect = pygame.Rect(yes_button_x, yes_button_y, yes_button_width, yes_button_height)
            pygame.draw.rect(self.screen, YES_COLOR, yes_button_rect)
            pygame.draw.rect(self.screen, (30, 100, 30), yes_button_rect, 2)

            yes_text = self.button_font.render("YES", True, BUTTON_TEXT_COLOR)
            self.screen.blit(yes_text, (yes_button_x + yes_button_width // 2 - yes_text.get_width() // 2,
                                       yes_button_y + yes_button_height // 2 - yes_text.get_height() // 2))

            # No button
            no_button_width = 80
            no_button_height = 40
            no_button_x = WIDTH // 4 + 10 if player == 0 else 3 * WIDTH // 4 - no_button_width // 2
            no_button_y = HEIGHT // 2 + 40

            no_button_rect = pygame.Rect(no_button_x, no_button_y, no_button_width, no_button_height)
            pygame.draw.rect(self.screen, NO_COLOR, no_button_rect)
            pygame.draw.rect(self.screen, (100, 30, 30), no_button_rect, 2)

            no_text = self.button_font.render("NO", True, BUTTON_TEXT_COLOR)
            self.screen.blit(no_text, (no_button_x + no_button_width // 2 - no_text.get_width() // 2,
                                      no_button_y + no_button_height // 2 - no_text.get_height() // 2))

        # Check responses and show appropriate message
        if all(response is not None for response in player_response):
            if all(player_response):
                restart_text = self.title_font.render("Restarting Game...", True, (255, 215, 0))
                self.screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, 2 * HEIGHT // 3))
            elif any(not response for response in player_response):
                quit_text = self.title_font.render("Game Ending...", True, (255, 100, 100))
                self.screen.blit(quit_text, (WIDTH // 2 - quit_text.get_width() // 2, 2 * HEIGHT // 3))

    def draw_game_ending(self, ending_message):
        # Draw semi-transparent overlay
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))

        # Draw ending message
        text = self.title_font.render(ending_message, True, (255, 100, 100))
        self.screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - 50))

        # Draw quit message
        quit_text = self.message_font.render("Game will exit in a few seconds...", True, (255, 255, 255))
        self.screen.blit(quit_text, (WIDTH // 2 - quit_text.get_width() // 2, HEIGHT // 2 + 20))

    def show_tutorial(self):
        # Draw semi-transparent overlay
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))

        # Draw tutorial title
        title_text = self.title_font.render("Gobblet Jr. Tutorial", True, (255, 215, 0))
        self.screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 50))

        # Draw rules
        rules = [
            "Object: Create a row of 3 of your pieces horizontally, vertically, or diagonally",
            "1. Each player has 6 pieces in 3 sizes (small, medium, large)",
            "2. Larger pieces can cover smaller pieces (gobble them)",
            "3. Covered pieces are still in play and can be revealed again",
            "4. You can only see the top piece in each cell",
            "5. A player wins by forming a row of 3 visible pieces",
            "",
            "Controls:",
            "- Click and drag pieces from your side panel to the board",
            "- You can also move pieces already on the board to new positions",
            "- Larger pieces can cover smaller ones (yours or opponent's)",
            "",
            "Press any key to start the game..."
        ]

        for i, rule in enumerate(rules):
            rule_text = self.message_font.render(rule, True, (255, 255, 255))
            self.screen.blit(rule_text, (WIDTH // 2 - rule_text.get_width() // 2, 120 + i * 35))

    def get_player_buttons(self, player):
        yes_button_width = 80
        yes_button_height = 40
        yes_button_x = WIDTH // 4 - yes_button_width // 2 if player == 0 else 3 * WIDTH // 4 - yes_button_width - 10
        yes_button_y = HEIGHT // 2 + 40

        no_button_width = 80
        no_button_height = 40
        no_button_x = WIDTH // 4 + 10 if player == 0 else 3 * WIDTH // 4 - no_button_width // 2
        no_button_y = HEIGHT // 2 + 40

        yes_button_rect = pygame.Rect(yes_button_x, yes_button_y, yes_button_width, yes_button_height)
        no_button_rect = pygame.Rect(no_button_x, no_button_y, no_button_width, no_button_height)

        return yes_button_rect, no_button_rect