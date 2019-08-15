class Piece:

    def __init__(self, team, piece_type, id = -1, castled=None, moved=False, defended_by = [], attacked_by = []):
        self.team = team
        self.piece_type = piece_type
        self.display_text = team + piece_type
        self.moved = moved
        self.id = id
        self.castled = castled
        self.defended_by = defended_by
        self.attacked_by = attacked_by

    def __copy__(self):
        copy_defended_by = list(map(lambda pos: [pos[0], pos[1]], self.defended_by))
        copy_attacked_by = list(map(lambda pos: [pos[0], pos[1]], self.attacked_by))
        return Piece(self.team, self.piece_type, self.id, self.castled, self.moved, copy_defended_by, copy_attacked_by)