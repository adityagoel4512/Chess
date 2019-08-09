import piece as chess_piece

class Board:
    grid = []
    rows = 8
    colors = ['W', 'B']
    pieces = ['P', 'R', 'H', 'B', 'Q', 'K']

    # TODO: start searching computerised player
    # scores = []
    # dead_pieces = []
    # piece_value_map = map([...])

    def __init__(self, grid = None, king_pos = [[7, 4], [0, 4]], move_count = 0):
        self.king_pos = king_pos
        self.move_count = move_count
        if grid is None:
            for i in range(self.rows):
                self.grid.append([])
                for j in range(self.rows):
                    self.grid[i].append([self.colors[(i+j)%2], None])
        else:
            self.grid = grid

    def __deepcopy__(self, memodict={}):
        copy_grid = []
        for row in range(self.rows):
            copy_grid.append([])
            for col in range(self.rows):
                piece = self.get_piece(row, col)
                if piece is not None:
                    copy_grid[row].append([self.grid[row][col][0], piece.__copy__()])
                else:
                    copy_grid[row].append([self.grid[row][col][0], None])

        copy_king_pos = list(map(lambda pos : [pos[0], pos[1]], self.king_pos))
        return Board(copy_grid, copy_king_pos, self.move_count)

    def clear_board(self):
        for row in self.grid:
            for i in range(self.rows):
                row[i][1] = None

    def in_range(self, row, column):
        return row < self.rows and row >= 0 and column < self.rows and column >= 0

    def get_piece(self, row, column):
        if not self.in_range(row, column):
            return None
        return self.grid[row][column][1]

    def set_piece(self, row, column, piece):
        assert(self.in_range(row, column))
        if piece is not None and piece.piece_type == 'K':
            self.king_pos[self.colors.index(piece.team)] = [row, column]
        self.grid[row][column][1] = piece

    def move_piece(self, r1, c1, r2, c2, team, filter_check_moves):
        piece = self.get_piece(r1, c1)
        valid_moves = self.compute_valid_moves(r1, c1, team, filter_check_moves)

        if len(list(filter(lambda move: move == [r2, c2], valid_moves))) == 0:
            print("Invalid move")
            return False

        destination = self.get_piece(r2, c2)

        self.set_piece(r1, c1, None)
        self.set_piece(r2, c2, piece)

        if destination is not None and destination.piece_type == 'K':
            print(piece.team + " wins!\n")

        self.move_count += 1
        piece.moved = True

        return piece.moved

    def setup_pieces(self):
        for i in range(self.rows):
            self.set_piece(6, i, chess_piece.Piece('W', 'P'))
            self.set_piece(1, i, chess_piece.Piece('B', 'P'))

        # Rooks, Horses, Bishops
        i = 0
        while i < 3:
            self.set_piece(0, i, chess_piece.Piece('B', self.pieces[i+1]))
            self.set_piece(0, self.rows-(i+1), chess_piece.Piece('B', self.pieces[i+1]))
            self.set_piece(self.rows-1, i, chess_piece.Piece('W', self.pieces[i+1]))
            self.set_piece(self.rows-1, self.rows-(i+1), chess_piece.Piece('W', self.pieces[i+1]))
            i += 1

        # Queen
        self.set_piece(0, 3, chess_piece.Piece('B', self.pieces[4]))
        self.set_piece(self.rows-1, 3, chess_piece.Piece('W', self.pieces[4]))

        # King
        self.set_piece(0, 4, chess_piece.Piece('B', self.pieces[5]))
        self.set_piece(self.rows-1, 4, chess_piece.Piece('W', self.pieces[5]))

    def position_in_check(self, side):

        i = self.colors.index(side)
        r1 = self.king_pos[i][0]
        c1 = self.king_pos[i][1]

        king_piece = self.get_piece(r1, c1)
        for row in range(self.rows):
            for col in range(self.rows):
                temp_piece = self.get_piece(row, col)
                if temp_piece is not None and temp_piece.team != king_piece.team:
                    if len(list(filter(lambda pos : pos == [r1, c1], self.compute_valid_moves(row, col, temp_piece.team, False)))) > 0:
                        return True

        return False

    def check_checkmate(self, side):

        i = self.colors.index(side)
        r1 = self.king_pos[i][0]
        c1 = self.king_pos[i][1]

        king = self.get_piece(r1, c1)

        if not self.position_in_check(side):
            return False
        for row in range(self.rows):
            for col in range(self.rows):
                piece = self.get_piece(row, col)
                if piece is not None and piece.team == king.team:
                    moves = self.compute_valid_moves(row, col, piece.team, False)
                    for move in moves:
                        temp_state = self.__deepcopy__()
                        temp_state.move_piece(row, col, move[0], move[1], piece.team, False)
                        if not temp_state.position_in_check(side):
                            return False
        return True

    def results_in_check(self, r1, c1, move, filter_check_moves):
        assert self.get_piece(r1, c1) is not None
        temp_state = self.__deepcopy__()
        temp_state.move_piece(r1, c1, move[0], move[1], temp_state.get_piece(r1, c1).team, filter_check_moves)
        return temp_state.position_in_check(self.get_piece(r1, c1).team)

    def compute_valid_moves(self, r1, c1, team, filter_check_moves):

        piece = self.get_piece(r1, c1)
        valid_moves = []

        if piece is None or piece.team != team:
            return valid_moves

        direction = 1 if piece.team == 'B' else -1

        if piece.piece_type == 'P':
            if self.get_piece(r1 + (direction * 1), c1) is None:
                valid_moves.append([r1 + (direction * 1), c1])
            if not piece.moved and self.get_piece(r1 + (direction * 2), c1) is None:
                valid_moves.append([r1 + (direction * 2), c1])

            top_right = self.get_piece(r1 + (direction * 1), c1 + 1)
            top_left = self.get_piece(r1 + (direction * 1), c1 - 1)

            if top_right is not None and top_right.team != piece.team:
                valid_moves.append([r1 + (direction * 1), c1 + 1])
            if top_left is not None and top_left.team != piece.team:
                valid_moves.append([r1 + (direction * 1), c1 - 1])

        if piece.piece_type == 'R' or piece.piece_type == 'Q':
            signs = [[1, 0], [0, 1], [-1, 0], [0, -1]]

            for sign in signs:
                i = 1
                while self.in_range(r1 + (sign[0] * i), c1 + (sign[1] * i)) and self.get_piece(r1 + (sign[0] * i), c1 + (sign[1] * i)) is None:
                    valid_moves.append([r1 + (sign[0] * i), c1 + (sign[1] * i)])
                    i += 1
                if self.in_range(r1 + (sign[0] * i), c1 + (sign[1] * i)) and self.get_piece(r1 + (sign[0] * i), c1 + (sign[1] * i)).team != piece.team:
                    valid_moves.append([r1 + (sign[0] * i), c1 + (sign[1] * i)])


        if piece.piece_type == 'H':
            signs = [[1, 1], [1, -1], [-1, 1], [-1, -1]]

            for sign in signs:
                if self.in_range(r1 + (sign[0] * 1), c1 + (sign[1] * 2)) and (self.get_piece(r1 + (sign[0] * 1), c1 + (sign[1] * 2)) is None or self.get_piece(r1 + (sign[0] * 1), c1 + (sign[1] * 2)).team != piece.team):
                    valid_moves.append([r1 + (sign[0] * 1), c1 + (sign[1] * 2)])
                if self.in_range(r1 + (sign[0] * 2), c1 + (sign[1] * 1)) and (self.get_piece(r1 + (sign[0] * 2), c1 + (sign[1] * 1)) is None or self.get_piece(r1 + (sign[0] * 2), c1 + (sign[1] * 1)).team != piece.team):
                    valid_moves.append([r1 + (sign[0] * 2), c1 + (sign[1] * 1)])


        if piece.piece_type == 'B' or piece.piece_type == 'Q':
            signs = [[1, 1], [1, -1], [-1, 1], [-1, -1]]

            for sign in signs:
                i = 1
                while self.in_range(r1 + (sign[0] * i), c1 + (sign[1] * i)) and self.get_piece(r1 + (sign[0] * i), c1 + (sign[1] * i)) is None:
                    valid_moves.append([r1 + (sign[0] * i), c1 + (sign[1] * i)])
                    i += 1

                if self.in_range(r1 + (sign[0] * i), c1 + (sign[1] * i)) and self.get_piece(r1 + (sign[0] * i), c1 + (sign[1] * i)).team != piece.team:
                    valid_moves.append([r1 + (sign[0] * i), c1 + (sign[1] * i)])

        if piece.piece_type == 'K':
            # Disallow moves that result in check
            for row in range(r1 - 1, r1 + 2):
                for col in range(c1 - 1, c1 + 2):
                    if self.in_range(row, col) and (self.get_piece(row, col) is None or self.get_piece(row, col).team != piece.team):
                        valid_moves.append([row, col])

        # TODO: filter out moves that lead to check
        if filter_check_moves:
            valid_moves = list(filter(lambda move : not self.results_in_check(r1, c1, move, not filter_check_moves), valid_moves))

        return valid_moves

    def evaluate_score(self, team, maximiser=True):
        centipawn_piece_dict = {'P': 100, 'H': 350, 'B': 350, 'R': 525, 'Q': 1000, 'K': 10000}
        material_balance = 0
        positional_balance = 0
        for row in range(self.rows):
            for col in range(self.rows):
                piece = self.get_piece(row, col)
                if piece is None:
                    print("NONE")
                elif piece.team == team:
                    material_balance += centipawn_piece_dict[piece.piece_type]
                elif piece.team != team:
                    material_balance -= centipawn_piece_dict[piece.piece_type]
        total_balance = material_balance + positional_balance
        return total_balance if maximiser else -total_balance

    def search_game_tree(self, start_team, moves, game_boards):
        if moves == 0:
            return
        opponent_team = self.colors[(self.colors.index(start_team) + 1) % len(self.colors)]
        for row in range(self.rows):
            for col in range(self.rows):
                piece = self.get_piece(row, col)
                if piece is not None and piece.team == start_team:
                    valid_moves = self.compute_valid_moves(row, col, start_team, True)
                    for move in valid_moves:
                        temp_state = self.__deepcopy__()
                        temp_state.move_piece(row, col, move[0], move[1], start_team, True)
                        if moves == 1:
                            game_boards.append(temp_state)
                        temp_state.search_game_tree(opponent_team, moves-1, game_boards)

    def play_game(self, mode=0):

        if mode == 0:
            while not self.check_checkmate(board.colors[self.move_count % 2]):
                self.display_board()
                print(board.colors[self.move_count % 2] + "'s move:")
                r1, c1, r2, c2 = input("Enter coordinates of moves").split()
                self.move_piece(int(r1), int(c1), int(r2), int(c2), board.colors[self.move_count % 2], True)
        else:
            print('computer')
            # implement computer play here

    def display_board(self):
        print('\n')
        for i in range(self.rows):
            row = map(lambda pos : pos if pos[1] is None else [pos[0], pos[1].display_text] , self.grid[i])
            print(*row)
        print('\n')

if __name__ == "__main__":
    board = Board()
    board.setup_pieces()
    board.play_game()
    # two_moves = []
    # board.search_game_tree('W', 2, two_moves)
    # print(len(two_moves))



    # board.display_board()
    print('Done')
