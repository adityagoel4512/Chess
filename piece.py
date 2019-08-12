class Piece:

    def __init__(self, team, piece_type, id = -1, moved=False):
        self.team = team
        self.piece_type = piece_type
        self.display_text = team + piece_type
        self.moved = moved
        self.id = id

    def __copy__(self):
        return Piece(self.team, self.piece_type, self.id, self.moved)