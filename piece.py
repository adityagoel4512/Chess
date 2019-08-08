class Piece:

    def __init__(self, team, piece_type):
        self.team = team
        self.piece_type = piece_type
        self.display_text = team + piece_type
        self.moved = False

    def __copy__(self):
        return Piece(self.team, self.piece_type)