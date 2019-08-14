class Piece:

    def __init__(self, team, piece_type, id = -1, castled=None, moved=False, defended_by = []):
        self.team = team
        self.piece_type = piece_type
        self.display_text = team + piece_type
        self.moved = moved
        self.id = id
        self.defended_by = defended_by
        self.castled = castled

    def __copy__(self):
        copy_defended_by = list(map(lambda pos: [pos[0], pos[1]], self.defended_by))
        return Piece(self.team, self.piece_type, self.id, self.castled, self.moved, copy_defended_by)