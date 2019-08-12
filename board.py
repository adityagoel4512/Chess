import piece as chess_piece
import piece_square_tables as tables

class Board:
    grid = []
    rows = 8
    colors = ['W', 'B']
    pieces = ['P', 'R', 'H', 'B', 'Q', 'K']


    def __init__(self, grid=None, king_pos=[[7, 4], [0, 4]], move_count=0, castling = {'W': [False, False], 'B': [False, False]}, dead_pieces = {'W': [], 'B': []}):
        self.king_pos = king_pos
        self.move_count = move_count
        # King side 2nd element, Queen side 1st element.
        self.castling = castling
        self.dead_pieces = dead_pieces
        if grid is None:
            for i in range(self.rows):
                self.grid.append([])
                for j in range(self.rows):
                    self.grid[i].append([self.colors[(i + j) % 2], None])
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

        copy_king_pos = list(map(lambda pos: [pos[0], pos[1]], self.king_pos))
        copy_castling = {'W': list(map(lambda castle: castle, self.castling['W'])), 'B': list(map(lambda castle: castle, self.castling['B']))}
        copy_dead_pieces = {'W': list(map(lambda piece: piece.__copy__(), self.dead_pieces['W'])), 'B': list(map(lambda piece: piece.__copy__(), self.dead_pieces['B']))}
        return Board(copy_grid, copy_king_pos, self.move_count, copy_castling, copy_dead_pieces)

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
        assert (self.in_range(row, column))
        if piece is not None and piece.piece_type == 'K':
            self.king_pos[self.colors.index(piece.team)] = [row, column]
        self.grid[row][column][1] = piece

    def move_piece(self, r1, c1, r2, c2, team, filter_check_moves):
        piece = self.get_piece(r1, c1)
        valid_moves = self.compute_valid_moves(r1, c1, team, filter_check_moves)

        if len(list(filter(lambda move: move == [r2, c2], valid_moves))) == 0:
            # print("Invalid move")
            return False


        destination = self.get_piece(r2, c2)

        # No valid moves replace a piece with its own team member
        if destination is not None:
            self.dead_pieces[destination.team].append(destination)

        self.set_piece(r1, c1, None)
        self.set_piece(r2, c2, piece)

        if c2 - c1 == 2 and piece.piece_type == 'K':
            # King Side Castle
            rook = self.get_piece(r1, self.rows-1)
            self.set_piece(r1, self.rows-1, None)
            self.set_piece(r1, c2-1, rook)
        elif c2 - c1 == -2 and piece.piece_type == 'K':
            rook = self.get_piece(r1, 0)
            self.set_piece(r1, 0, None)
            self.set_piece(r1, c2+1, rook)

        self.move_count += 1
        piece.moved = True

        return piece.moved

    def setup_pieces(self):
        for i in range(self.rows):
            self.set_piece(6, i, chess_piece.Piece('W', 'P', i))
            self.set_piece(1, i, chess_piece.Piece('B', 'P', i))

        # Rooks, Horses, Bishops
        i = 0
        while i < 3:
            self.set_piece(0, i, chess_piece.Piece('B', self.pieces[i + 1], i))
            self.set_piece(0, self.rows - (i + 1), chess_piece.Piece('B', self.pieces[i + 1], i+4))
            self.set_piece(self.rows - 1, i, chess_piece.Piece('W', self.pieces[i + 1], i))
            self.set_piece(self.rows - 1, self.rows - (i + 1), chess_piece.Piece('W', self.pieces[i + 1], i+4))
            i += 1

        # Queen
        self.set_piece(0, 3, chess_piece.Piece('B', self.pieces[4], 1))
        self.set_piece(self.rows - 1, 3, chess_piece.Piece('W', self.pieces[4], 0))

        # King
        self.set_piece(0, 4, chess_piece.Piece('B', self.pieces[5], 1))
        self.set_piece(self.rows - 1, 4, chess_piece.Piece('W', self.pieces[5], 0))

    def locate_piece(self, piece):
        assert piece is not None
        for row in range(self.rows):
            for col in range(self.rows):
                square = self.get_piece(row, col)
                if square is not None and piece.id == square.id and square.display_text == piece.display_text:
                    return [row, col]
        return [-1, -1]

    def position_in_check(self, side):
        i = self.colors.index(side)
        r1 = self.king_pos[i][0]
        c1 = self.king_pos[i][1]

        king_piece = self.get_piece(r1, c1)

        if king_piece is None:
            return True

        for row in range(self.rows):
            for col in range(self.rows):
                temp_piece = self.get_piece(row, col)
                # print(temp_piece, king_piece)
                if temp_piece is not None and temp_piece.team != king_piece.team:
                    if len(list(filter(lambda pos: pos == [r1, c1], self.compute_valid_moves(row, col, temp_piece.team, False)))) > 0:
                        # print('check')
                        # print(king_piece)
                        # print(self.king_pos)
                        # self.display_board()
                        return True

        return False

    def check_checkmate(self, side):
        i = self.colors.index(side)
        r1 = self.king_pos[i][0]
        c1 = self.king_pos[i][1]

        king = self.get_piece(r1, c1)
        if king is None:
            return True

        if not self.position_in_check(side):
            return False
        for row in range(self.rows):
            for col in range(self.rows):
                piece = self.get_piece(row, col)
                if piece is not None and piece.team == king.team:
                    moves = self.compute_valid_moves(row, col, piece.team, False)
                    for move in moves:
                        if self.move_piece(row, col, move[0], move[1], piece.team, False):
                            if not self.position_in_check(side):
                                return False
                            moved_piece = self.get_piece(move[0], move[1])
                            self.set_piece(row, col, moved_piece)
                            self.set_piece(move[0], move[1], None)
        return True

    def results_in_check(self, r1, c1, move, filter_check_moves):
        piece = self.get_piece(r1, c1)
        assert piece is not None
        temp_state = self.__deepcopy__()
        temp_state.move_piece(r1, c1, move[0], move[1], piece.team, filter_check_moves)

        # Checking for check post castling
        if piece.piece_type == 'K':
            if move[1] - c1 == 2:
                # King side
                temp_state.set_piece(r1, c1-1, temp_state.get_piece(r1, self.rows-1))
                temp_state.set_piece(r1, self.rows-1, None)
            elif move[1] - c1 == 2:
                # Queen side
                temp_state.set_piece(r1, c1+1, temp_state.get_piece(r1, 0))
                temp_state.set_piece(r1, 0, None)
        return temp_state.in_range(move[0], move[1]) and temp_state.position_in_check(piece.team)

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
                while self.in_range(r1 + (sign[0] * i), c1 + (sign[1] * i)) and self.get_piece(r1 + (sign[0] * i),
                                                                                               c1 + (sign[
                                                                                                         1] * i)) is None:
                    valid_moves.append([r1 + (sign[0] * i), c1 + (sign[1] * i)])
                    i += 1
                if self.in_range(r1 + (sign[0] * i), c1 + (sign[1] * i)) and self.get_piece(r1 + (sign[0] * i), c1 + (
                        sign[1] * i)).team != piece.team:
                    valid_moves.append([r1 + (sign[0] * i), c1 + (sign[1] * i)])

        if piece.piece_type == 'H':
            signs = [[1, 1], [1, -1], [-1, 1], [-1, -1]]

            for sign in signs:
                if self.in_range(r1 + (sign[0] * 1), c1 + (sign[1] * 2)) and (
                        self.get_piece(r1 + (sign[0] * 1), c1 + (sign[1] * 2)) is None or self.get_piece(
                    r1 + (sign[0] * 1), c1 + (sign[1] * 2)).team != piece.team):
                    valid_moves.append([r1 + (sign[0] * 1), c1 + (sign[1] * 2)])
                if self.in_range(r1 + (sign[0] * 2), c1 + (sign[1] * 1)) and (
                        self.get_piece(r1 + (sign[0] * 2), c1 + (sign[1] * 1)) is None or self.get_piece(
                    r1 + (sign[0] * 2), c1 + (sign[1] * 1)).team != piece.team):
                    valid_moves.append([r1 + (sign[0] * 2), c1 + (sign[1] * 1)])

        if piece.piece_type == 'B' or piece.piece_type == 'Q':
            signs = [[1, 1], [1, -1], [-1, 1], [-1, -1]]

            for sign in signs:
                i = 1
                while self.in_range(r1 + (sign[0] * i), c1 + (sign[1] * i)) and self.get_piece(r1 + (sign[0] * i),
                                                                                               c1 + (sign[
                                                                                                         1] * i)) is None:
                    valid_moves.append([r1 + (sign[0] * i), c1 + (sign[1] * i)])
                    i += 1

                if self.in_range(r1 + (sign[0] * i), c1 + (sign[1] * i)) and self.get_piece(r1 + (sign[0] * i), c1 + (
                        sign[1] * i)).team != piece.team:
                    valid_moves.append([r1 + (sign[0] * i), c1 + (sign[1] * i)])

        if piece.piece_type == 'K':
            # Disallow moves that result in check
            for row in range(r1 - 1, r1 + 2):
                for col in range(c1 - 1, c1 + 2):
                    if self.in_range(row, col) and (self.get_piece(row, col) is None
                                                    or self.get_piece(row, col).team != piece.team):
                        valid_moves.append([row, col])

            # Castling

            if piece.moved:
                self.castling[team] = [True, True]
            else:
                # King side
                for col in range(c1+1, self.rows-1):
                    if self.get_piece(r1, col) is not None:
                        self.castling[team][1] = False
                        pass
                far_right_piece = self.get_piece(r1, self.rows-1)
                self.castling[team][1] = self.castling[team][1] and far_right_piece is not None and far_right_piece.piece_type == 'R' and far_right_piece.team == team and not far_right_piece.moved
                # Queen side
                for col in range(1, c1):
                    if self.get_piece(r1, col) is not None:
                        self.castling[team][0] = False
                        pass
                far_left_piece = self.get_piece(r1, 0)
                self.castling[team][0] = self.castling[team][0] and far_left_piece is not None and far_left_piece.piece_type == 'R' and far_left_piece.team == team and not far_left_piece.moved

                if self.castling[team][1]:
                    valid_moves.append([r1, c1+2])
                if self.castling[team][0]:
                    valid_moves.append([r1, c1-2])

        if filter_check_moves:
            valid_moves = list(
                filter(lambda move: self.in_range(move[0], move[1]) and not self.results_in_check(r1, c1, move, not filter_check_moves), valid_moves))

        return valid_moves

    def evaluate_score(self, team):
        # TODO: Three stage evaluation:
        # TODO: Stage 1: material and pawn-king structure
        # TODO: Stage 2: dynamic piece-square tables
        # TODO: Stage 3: mobility and board control (no of available moves high is valuable)
        further_moves = []
        self.search_game_tree(team, 1, further_moves)
        mobility_score = len(further_moves) * 2

        material_balance = 0
        positional_balance = 0
        bishop_count = 0

        # If black piece table needs to be vertically reflected and horizontally reflected

        for row in range(self.rows):
            for col in range(self.rows):
                piece = self.get_piece(row, col)
                color_based_access = [[row, col], [7-row, 7-col]] if team == 'W' else [[7-row, 7-col], [row, col]]
                if piece is None:
                    pass
                elif piece.team == team:
                    material_balance += tables.centipawn_piece_dict[piece.piece_type]
                    positional_balance += tables.centipawn_position_dict[piece.piece_type][color_based_access[0][0]][color_based_access[0][1]]
                    if piece.piece_type == 'B':
                        bishop_count += 1
                    if row > 1 and row < 6 and col > 1 and col < 6:
                        positional_balance += 15
                elif piece.team != team:
                    material_balance -= tables.centipawn_piece_dict[piece.piece_type]
                    positional_balance -= tables.centipawn_position_dict[piece.piece_type][color_based_access[1][0]][color_based_access[1][1]]
                    if piece.piece_type == 'B':
                        bishop_count -= 1
                    if row > 1 and row < 6 and col > 1 and col < 6:
                        positional_balance -= 15

        if bishop_count == 2 or bishop_count == -2:
            material_balance += (bishop_count * 25)

        return material_balance + positional_balance + mobility_score

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
                        if moves == 1 and temp_state is not None:
                            game_boards.append(temp_state)
                        temp_state.search_game_tree(opponent_team, moves - 1, game_boards)

    def minimax(self, depth, team, maximiser, alpha=float('-inf'), beta=float('inf')):
        opposition_team = self.colors[(self.colors.index(team)+1)%2]
        if depth == 0 or self.check_checkmate(team) or self.check_checkmate(opposition_team):
            return self
        boards = []
        self.search_game_tree(team, 1, boards)
        if maximiser:
            max_value = float('-inf')
            max_board = None
            for board in boards:
                minimax_board = board.minimax(depth-1, opposition_team, not maximiser, alpha, beta)
                board_score = minimax_board.evaluate_score(team)
                if board_score > max_value:
                    max_value = board_score
                    max_board = board
                alpha = max(alpha, max_value)
                if beta <= alpha:
                    break
            return max_board
        else:
            min_value = float('-inf')
            min_board = None
            for board in boards:
                minimax_board = board.minimax(depth-1, opposition_team, not maximiser, alpha, beta)
                board_score = minimax_board.evaluate_score(team)
                if board_score > min_value:
                    min_value = board_score
                    min_board = minimax_board
                beta = min(beta, min_value)
                if beta <= alpha:
                    break
            return min_board

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
            row = map(lambda pos: pos if pos[1] is None else [pos[0], pos[1].display_text], self.grid[i])
            print(*row)
        print('\n')

def differences_between_boards(b1, b2):
    differences = []
    for row in range(b2.rows):
        for col in range(b2.rows):
            piece2 = b2.get_piece(row, col)
            piece1 = b1.get_piece(row, col)
            if piece1 is not None and piece2 is None:
                #  moved from row, col to somewhere
                dest = b2.locate_piece(piece1)
                differences.append([(row, col), (dest[0], dest[1])])
            elif piece1 is not None and piece2 is not None and piece1.display_text != piece2.display_text:
                src = b1.locate_piece(piece2)
                differences.append(['X', (src[0], src[1]), (row, col)])

    return differences


if __name__ == "__main__":
    board = Board()
    board.setup_pieces()

    i = 0
    while not board.check_checkmate(board.colors[i%2]):
        next_board = board.minimax(2, board.colors[i%2], True)
        next_board.display_board()
        # print(next_board.evaluate_score(board.colors[i%2]))
        print(differences_between_boards(board, next_board))
        print(board.colors[(i)%2] + "'s move. Move " + str(i+1) + ".")
        board = next_board
        i += 1


    print('Done')
