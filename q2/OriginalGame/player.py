from constants import *
from UI.piece import Piece
class Player:
    def __init__(self, player_id):
        self.player_id = player_id
        self.pieces = [(size, player_id) for size in PIECE_SIZES] * 2
    
    def remove_piece(self, size):
        self.pieces.remove((size, self.player_id))
    
    def has_piece_size(self, size):
        return (size, self.player_id) in self.pieces
    
    def render(self, screen, side_x):
        for i, (size, _) in enumerate(self.pieces):
            row, col = divmod(i, SIDE_GRID_COLS)
            x = side_x + SIDE_BOX_WIDTH // 2
            y = 100 + row * 100 + col * 50
            piece = Piece(size, self.player_id)
            piece.render(screen, x, y)