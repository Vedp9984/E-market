from colors import PLAYER_COLORS
import pygame
class Piece:
    def __init__(self, size, player):
        self.size = size
        self.player = player
    
    def render(self, screen, x, y):
        # Draw shadow
        pygame.draw.circle(screen, (100, 100, 100), (x + 3, y + 3), self.size)
        
        # Draw main circle
        pygame.draw.circle(screen, PLAYER_COLORS[self.player], (x, y), self.size)
        
        # Draw highlight
        highlight_radius = max(self.size - 5, self.size * 0.8)
        pygame.draw.circle(screen, (255, 255, 255, 100), (x - self.size//4, y - self.size//4), highlight_radius//2, 2)
