import pygame
import sys
import math
from colors import *
from constants import *
from UI.gameUI import GameUI
from UI.board import Board
from UI.piece import Piece
from player import Player
pygame.init()

class Game:
    def __init__(self):
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
        self.board = Board()
        self.players = [Player(0), Player(1)]
        self.turn = 0
        self.game_over = False
        self.draw_game = False
        self.player_response = [None, None]
        self.ui.error_message = "Game started! Player 1's turn."
    
    def handle_click(self, x, y):
        if self.game_over and not self.game_ending:
            # Check if yes/no buttons were clicked
            for player in [0, 1]:
                yes_button, no_button = self.ui.get_player_buttons(player)
                
                if yes_button.collidepoint(x, y) and self.player_response[player] is None:
                    self.player_response[player] = True
                elif no_button.collidepoint(x, y) and self.player_response[player] is None:
                    self.player_response[player] = False
                
                # If both players have responded
                if all(response is not None for response in self.player_response):
                    if all(self.player_response):
                        # Both said yes, restart the game after a delay
                        self.restart_timer = pygame.time.get_ticks() + 1500  # 1.5 seconds
                    else:
                        # At least one said no, end the game
                        self.game_ending = True
                        # Determine who didn't want to play
                        if not self.player_response[0] and not self.player_response[1]:
                            self.ending_message = "Both players decided to quit"
                        elif not self.player_response[0]:
                            self.ending_message = "Player 1 decided to quit"
                        else:
                            self.ending_message = "Player 2 decided to quit"
                        self.end_timer = pygame.time.get_ticks() + 3000  # 3 seconds
        
        elif not self.game_over and not self.game_ending:
            # Check for dragging from side boxes
            for player in [0, 1]:
                for i, (size, p) in enumerate(self.players[player].pieces):
                    side_x = 0 if player == 0 else WIDTH - SIDE_BOX_WIDTH
                    row, col = divmod(i, SIDE_GRID_COLS)
                    center_x = side_x + SIDE_BOX_WIDTH // 2
                    center_y = 100 + row * 100 + col * 50
                    
                    # Check if piece was clicked
                    if (x - center_x) ** 2 + (y - center_y) ** 2 <= size ** 2:
                        self.ui.dragging_piece = (size, player, "side", i)
                        break
            
            # Check for dragging from board
            if not self.ui.dragging_piece and SIDE_BOX_WIDTH <= x <= WIDTH - SIDE_BOX_WIDTH:
                col = (x - SIDE_BOX_WIDTH) // CELL_SIZE
                row = y // CELL_SIZE
                
                if 0 <= row < ROWS and 0 <= col < COLS and self.board.grid[row][col]:
                    size, player = self.board.grid[row][col][-1]
                    center_x = SIDE_BOX_WIDTH + col * CELL_SIZE + CELL_SIZE // 2
                    center_y = row * CELL_SIZE + CELL_SIZE // 2
                    
                    if (x - center_x) ** 2 + (y - center_y) ** 2 <= size ** 2:
                        self.ui.dragging_piece = (size, player, "board", (row, col))
    
    def handle_drop(self, x, y):
        if self.ui.dragging_piece:
            size, player, origin_type, origin_index = self.ui.dragging_piece
            if self.board.check_winner(player):
                self.game_over = True
                self.ui.error_message = f"Player {player + 1} wins! Play again?"
                return True
            if player != self.turn:
                self.ui.error_message = "Not your turn!"
                return False

            # Dropped inside the board
            if SIDE_BOX_WIDTH <= x <= WIDTH - SIDE_BOX_WIDTH and 0 <= y <= HEIGHT:
                col = (x - SIDE_BOX_WIDTH) // CELL_SIZE
                row = y // CELL_SIZE
                
                # Ensure indices are within bounds
                if not (0 <= row < ROWS and 0 <= col < COLS):
                    self.ui.error_message = "Invalid position!"
                    return False

                # Create a piece object
                piece = Piece(size, player)

                # Check if move is valid
                if self.board.is_valid_move(piece, row, col):
                    # Remove from original position
                    if origin_type == "side":
                        self.players[player].remove_piece(size)
                    elif origin_type == "board":
                        self.board.remove_top_piece(origin_index[0], origin_index[1])
                    
                    # Place on new position
                    self.board.place_piece(piece, row, col)

                    # Check for winner
                    if self.board.check_winner(player):
                        self.game_over = True
                        self.ui.error_message = f"Player {player + 1} wins! Play again?"
                        return True
                    
                    # Check for draw
                    if self.board.check_draw():
                        self.game_over = True
                        self.draw_game = True
                        self.ui.error_message = "Game is a draw! Play again?"
                        return True
                    
                    self.turn = 1 - self.turn  # Switch turn
                    self.ui.error_message = ""
                    return True  # Move successful
                else:
                    self.ui.error_message = "Invalid move: Cannot place on a larger piece!"

            # Return piece to original position if move is invalid
            if origin_type == "board":
                # The piece was removed above, add it back if move was invalid
                piece = Piece(size, player)
                self.board.place_piece(piece, origin_index[0], origin_index[1])

        return False
    
    def update(self):
        # Get mouse position for hover effect
        mouse_x, mouse_y = pygame.mouse.get_pos()
        
        # Update hover cell
        if (SIDE_BOX_WIDTH <= mouse_x <= WIDTH - SIDE_BOX_WIDTH and 
            0 <= mouse_y <= HEIGHT and not self.game_over and not self.game_ending and not self.tutorial_active):
            col = (mouse_x - SIDE_BOX_WIDTH) // CELL_SIZE
            row = mouse_y // CELL_SIZE
            if 0 <= row < ROWS and 0 <= col < COLS:
                self.ui.hover_cell = (row, col)
            else:
                self.ui.hover_cell = None
        else:
            self.ui.hover_cell = None
        
        # Check if it's time to restart
        if self.restart_timer and pygame.time.get_ticks() >= self.restart_timer:
            self.reset()
            self.restart_timer = None
        
        # Check if it's time to end the game
        if self.end_timer and pygame.time.get_ticks() >= self.end_timer:
            return False  # End the game
        
        return True  # Continue running
    
    def render(self):
        # Fill background
        self.ui.screen.fill(BACKGROUND)
        
        if not self.tutorial_active:
            self.board.render(self.ui.screen, self.ui.hover_cell)
            self.ui.draw_side_boxes(self.players, self.turn, self.game_over, self.game_ending)
            self.ui.draw_dragging_piece()
            self.ui.display_message(self.game_ending)
            
            if self.game_over and not self.game_ending:
                self.ui.draw_game_over(self.draw_game, self.turn, self.player_response)
            
            if self.game_ending:
                self.ui.draw_game_ending(self.ending_message)
        else:
            self.ui.show_tutorial()
        
        # Update the display
        pygame.display.flip()
    
    def run(self):
        running = True
        
        while running:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                elif self.tutorial_active and (event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN):
                    self.tutorial_active = False
                    self.ui.error_message = "Game started! Player 1's turn."
                
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not self.tutorial_active:
                    self.handle_click(event.pos[0], event.pos[1])
                
                elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    if self.ui.dragging_piece and not self.game_over and not self.game_ending and not self.tutorial_active:
                        self.handle_drop(event.pos[0], event.pos[1])
                        self.ui.dragging_piece = None
            
            # Update game state
            running = self.update() and running
            
            # Render the game
            self.render()
            
            # Cap the framerate
            pygame.time.delay(20)  # Simple way to limit to ~50 FPS
        
        pygame.quit()
        sys.exit()

# Create and run the game
if __name__ == "__main__":
    game = Game()
    game.run()