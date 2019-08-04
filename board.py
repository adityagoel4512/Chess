class Piece:
    display_text = None
    team = None
    piece_type = None
    moved = None 

    def __init__(self, team, piece_type):
        self.team = team
        self.piece_type = piece_type
        self.display_text = team + piece_type
        self.moved = False
        

class Board:
    grid = []
    rows = 8
    colors = ['W', 'B']
    pieces = ['P', 'R', 'H', 'B', 'Q', 'K']

    def __init__(self):
        for i in range(self.rows):
            self.grid.append([])
            for j in range(self.rows):
                self.grid[i].append([self.colors[(i+j)%2], None])

    def in_range(self, row, column):
        return row < self.rows and row >= 0 and column < self.rows and column >= 0
    
    def get_piece(self, row, column):
        if (not self.in_range(row, column)):
            return None
        return self.grid[row][column][1]

    def set_piece(self, row, column, piece):
        assert(self.in_range(row, column))
        self.grid[row][column][1] = piece

    def setup_pieces(self):
        for i in range(self.rows):
            self.set_piece(6, i, Piece('W', 'P'))
            self.set_piece(1, i, Piece('B', 'P'))
        
        i = 0
        # Rooks, Horses, Bishops

        while (i < 3):
            self.set_piece(0, i, Piece('B', self.pieces[i+1]))
            self.set_piece(0, self.rows-(i+1), Piece('B', self.pieces[i+1]))
            self.set_piece(self.rows-1, i, Piece('W', self.pieces[i+1]))
            self.set_piece(self.rows-1, self.rows-(i+1), Piece('W', self.pieces[i+1]))
            i += 1

        # Queen
        self.set_piece(0, 3, Piece('B', self.pieces[4]))
        self.set_piece(self.rows-1, 3, Piece('W', self.pieces[4]))

        # King
        self.set_piece(0, 4, Piece('B', self.pieces[5]))
        self.set_piece(self.rows-1, 4, Piece('W', self.pieces[5]))

    def compute_valid_moves(self, r1, c1):
        piece = self.get_piece(r1, c1)
        direction = 1 if piece.team == 'B' else -1
        valid_moves = []

        if (piece is None):
            return valid_moves
        
        if (piece.piece_type == 'P'):
            if (self.get_piece(r1 + (direction * 1), c1) is None):
                valid_moves.append([r1 + (direction * 1), c1])
            if (not piece.moved and self.get_piece(r1 + (direction * 2), c1) is None):
                valid_moves.append([r1 + (direction * 2), c1])
            top_right = self.get_piece(r1 + (direction * 1), c1 + 1)
            top_left = self.get_piece(r1 + (direction * 1), c1 - 1)
            if (top_right is not None and top_right.team != piece.team):
                valid_moves.append([r1 + (direction * 1), c1 + 1])
            if (top_left is not None and top_left.team != piece.team):
                valid_moves.append([r1 + (direction * 1), c1 - 1])

        elif (piece.piece_type == 'R'):
            # Check vertical
            i = 1
            while (self.in_range(r1 + (direction * i), c1) and self.get_piece(r1 + (direction * i), c1) is None):
                valid_moves.append([r1 + (direction * i), c1])
                i += 1
            if (self.in_range(r1 + (direction * i), c1) and self.get_piece(r1 + (direction * i), c1).team != piece.team):
                valid_moves.append([r1 + (direction * i), c1])

            # Check horizontal right
            i = 1
            while (self.in_range(r1, c1 + i) and self.get_piece(r1, c1 + i) is None):
                valid_moves.append([r1, c1 + i])
                i += 1
            if (self.in_range(r1, c1 + i) and self.get_piece(r1, c1 + i).team != piece.team):
                valid_moves.append([r1, c1 + i])

            # Check horizontal left
            i = 1
            while (self.in_range(r1, c1 - i) and self.get_piece(r1, c1 - i) is None):
                valid_moves.append([r1, c1 - i])
                i += 1
            if (self.in_range(r1, c1 - i) and self.get_piece(r1, c1 - i).team != piece.team):
                valid_moves.append([r1, c1 - i])
        return valid_moves

    def move_piece(self, r1, c1, r2, c2):
        piece = self.get_piece(r1, c1)
        destination = self.get_piece(r2, c2)
        # Check if valid move

        self.set_piece(r1, c1, None)
        self.set_piece(r2, c2, piece)
        piece.moved = True

    def display_board(self):
        print('\n')
        for i in range(self.rows):
            row = map(lambda pos : pos if pos[1] is None else [pos[0], pos[1].display_text] , self.grid[i])
            print(*row)
        print('\n')

if __name__ == "__main__":
    board = Board()
    board.setup_pieces()
    board.display_board()
    board.display_board()
    print(*board.compute_valid_moves(7, 0))
