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
    king_pos = None

    def __init__(self, grid = None):
        self.king_pos = [[7, 4], [0, 4]]
        if (grid is None):
            for i in range(self.rows):
                self.grid.append([])
                for j in range(self.rows):
                    self.grid[i].append([self.colors[(i+j)%2], None])
        else:
            self.grid = grid

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

        # Rooks, Horses, Bishops
        i = 0
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

    def position_in_check(self, r1, c1):
        king_piece = self.get_piece(r1, c1)
        for row in range(self.rows):
            for col in range(self.rows):
                temp_piece = self.get_piece(row, col)
                if (temp_piece is not None and temp_piece.team != king_piece.team):
                    if (len(list(filter(lambda pos : pos == [r1, c1], self.compute_valid_moves(row, col, temp_piece.team)))) > 0):
                        return True

        return False

    def check_checkmate(self, side):
        
        r1 = self.king_pos[0][0]
        c1 = self.king_pos[0][1]

        if (side == 'B'):
            r1 = self.king_pos[1][0]
            c1 = self.king_pos[1][1]

        king = self.get_piece(r1, c1)

        if (not self.position_in_check(r1, c1)):
            return False
        for row in range(self.rows):
            for col in range(self.rows):
                piece = self.get_piece(row, col)
                if (piece is not None and piece.team == king.team):
                    moves = self.compute_valid_moves(r1, c1)
                    for move in moves:
                        temp_state = Board(self.grid)
                        temp_state.move_piece(row, col, move[0], move[1], piece.team)
                        if (not temp_state.position_in_check(r1, c1)):
                            return False
        return True

    def compute_valid_moves(self, r1, c1, team):

        piece = self.get_piece(r1, c1)
        valid_moves = []

        if (piece is None or piece.team != team):
            return valid_moves
        
        direction = 1 if piece.team == 'B' else -1

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

        if (piece.piece_type == 'R' or piece.piece_type == 'Q'):
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

        if (piece.piece_type == 'H'):
            signs = [[1, 1], [1, -1], [-1, 1], [-1, -1]]
            
            for sign in signs:
                if (self.in_range(r1 + (sign[0] * 1), c1 + (sign[1] * 2)) and (self.get_piece(r1 + 1, c1 + 2) is None or self.get_piece(r1 + 1, c1 + 2).team != piece.team)):
                    valid_moves.append([r1 + (sign[0] * 1), c1 + (sign[1] * 2)])
                if (self.in_range(r1 + (sign[0] * 2), c1 + (sign[1] * 1)) and (self.get_piece(r1 + 2, c1 + 1) is None or self.get_piece(r1 + 2, c1 + 1).team != piece.team)):
                    valid_moves.append([r1 + (sign[0] * 2), c1 + (sign[1] * 1)])


        if (piece.piece_type == 'B' or piece.piece_type == 'Q'):
            signs = [[1, 1], [1, -1], [-1, 1], [-1, -1]]

            for sign in signs:
                i = 1
                while (self.in_range(r1 + (sign[0] * i), c1 + (sign[1] * i)) and self.get_piece(r1 + (sign[0] * i), c1 + (sign[1] * i)) is None):
                    valid_moves.append([r1 + (sign[0] * i), c1 + (sign[1] * i)])
                    i += 1
                
                if (self.in_range(r1 + (sign[0] * i), c1 + (sign[1] * i)) and self.get_piece(r1 + (sign[0] * i), c1 + (sign[1] * i)).team != piece.team):
                    valid_moves.append([r1 + (sign[0] * i), c1 + (sign[1] * i)])

        if (piece.piece_type == 'K'):
            # Disallow moves that result in check
            for row in range(r1-1, r1+1):
                for col in range(c1-1, c1+1):
                    if (self.in_range(row, col) and (self.get_piece(row, col) is None or self.get_piece(row, col).team != piece.team) and not self.position_in_check(r1, c1)): 
                        valid_moves.append([row, col])

        return valid_moves

    def move_piece(self, r1, c1, r2, c2, team):
        piece = self.get_piece(r1, c1)
        valid_moves = self.compute_valid_moves(r1, c1, team)

        if (len(list(filter(lambda move : move == [r2, c2], valid_moves))) == 0):
            print("Invalid move")
            return False
            
        destination = self.get_piece(r2, c2)

        self.set_piece(r1, c1, None)
        self.set_piece(r2, c2, piece)

        if (destination is not None and destination.piece_type == 'K'):
            print(piece.team + " wins!\n")

        if (piece.piece_type == 'K'):
            self.king_pos[self.colors.index(piece.team)] = [r2, c2]

        piece.moved = True

        return piece.moved
        
    def display_board(self):
        print('\n')
        for i in range(self.rows):
            row = map(lambda pos : pos if pos[1] is None else [pos[0], pos[1].display_text] , self.grid[i])
            print(*row)
        print('\n')

if __name__ == "__main__":
    board = Board()
    board.setup_pieces()
    move_count = 0

    while(not board.check_checkmate(board.colors[move_count % 2])):

        board.display_board()
        print(board.colors[move_count % 2] + "'s move:")
        r1, c1, r2, c2 = input("Enter coordinates of moves").split()
        if (board.move_piece(int(r1), int(c1), int(r2), int(c2), board.colors[move_count % 2])):
            move_count += 1

    print(*board.compute_valid_moves(0, 2, 'B'))
    print(board.check_checkmate('W'))
    print('Done')
