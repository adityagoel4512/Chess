import piece as chess_piece
import piece_square_tables as tables
import chess
import chess.svg

class Board:
    grid = []
    rows = 8
    colors = ['W', 'B']
    pieces = ['P', 'R', 'N', 'B', 'Q', 'K']

    def __init__(self, grid=None, king_pos=[[7, 4], [0, 4]], move_count=0,
                 can_castle={'W': [False, False], 'B': [False, False]},
                 dead_pieces={'W': [], 'B': []},
                 fifty_move_count=0):

        self.king_pos = king_pos
        self.move_count = move_count
        # King side 2nd element, Queen side 1st element.
        self.can_castle = can_castle
        self.dead_pieces = dead_pieces
        self.fifty_move_count = fifty_move_count
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
        copy_can_castle = {'W': list(map(lambda castle: castle, self.can_castle['W'])),
                           'B': list(map(lambda castle: castle, self.can_castle['B']))}
        copy_dead_pieces = {'W': list(map(lambda piece: piece.__copy__(), self.dead_pieces['W'])),
                            'B': list(map(lambda piece: piece.__copy__(), self.dead_pieces['B']))}
        copy_fifty_move_count = self.fifty_move_count
        return Board(copy_grid, copy_king_pos, self.move_count, copy_can_castle, copy_dead_pieces,
                     copy_fifty_move_count)

    def clear_board(self):
        for row in self.grid:
            for i in range(self.rows):
                row[i][1] = None

    def in_range(self, row, column):
        return self.rows > row >= 0 and self.rows > column >= 0

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

        if not filter(lambda move: move == [r2, c2], valid_moves):
            return False

        self.fifty_move_count += 1
        destination = self.get_piece(r2, c2)

        # No valid moves replace a piece with its own team member
        if destination is not None:
            destination.defended_by.clear()
            destination.attacked_by.clear()
            self.dead_pieces[destination.team].append(destination)
            self.fifty_move_count = 0

        self.set_piece(r1, c1, None)
        self.set_piece(r2, c2, piece)

        if c2 - c1 == 2 and piece.piece_type == 'K':
            # King Side Castle
            rook = self.get_piece(r1, self.rows - 1)
            self.set_piece(r1, self.rows - 1, None)
            self.set_piece(r1, c2 - 1, rook)
            piece.castled = True
        elif c2 - c1 == -2 and piece.piece_type == 'K':
            # Queen Side Castle
            rook = self.get_piece(r1, 0)
            self.set_piece(r1, 0, None)
            self.set_piece(r1, c2 + 1, rook)
            piece.castled = True
        if piece.piece_type == 'P':
            self.fifty_move_count = 0
            if r2 == self.rows or r2 == 0:
                # Promotion
                # TODO: pawn promotion as part of minimax not automatically choose highest value piece as done here
                # self.dead_pieces[team].append(piece)
                # print(self.dead_pieces[team])
                # revive_piece_text = input("Enter display text as desired for piece to reintroduce")
                # dead_pieces_display_texts = map(lambda p : p.display_text, self.dead_pieces[team])
                # while revive_piece_text not in dead_pieces_display_texts:
                #     revive_piece_text = input("Enter valid display text as desired for piece to reintroduce")
                # promotion_piece = filter(lambda p : p.display_text == revive_piece_text, self.dead_pieces[team])[0]
                # self.set_piece(r2, c2, promotion_piece)
                print('Promoting!')
                self.dead_pieces[team].append(piece)
                self.dead_pieces[team].sort(reverse=False, key=lambda p: tables.centipawn_piece_dict[p.piece_type])
                self.set_piece(r2, c2, self.dead_pieces[team][0])

        self.move_count += 1
        piece.moved = True
        piece.defended_by.clear()
        piece.attacked_by.clear()

        return piece.moved

    def setup_pieces(self):
        for i in range(self.rows):
            self.set_piece(6, i, chess_piece.Piece('W', 'P', i))
            self.set_piece(1, i, chess_piece.Piece('B', 'P', i))

        # Rooks, Knights, Bishops
        i = 0
        while i < 3:
            self.set_piece(0, i, chess_piece.Piece('B', self.pieces[i + 1], i))
            self.set_piece(0, self.rows - (i + 1), chess_piece.Piece('B', self.pieces[i + 1], i + 4))
            self.set_piece(self.rows - 1, i, chess_piece.Piece('W', self.pieces[i + 1], i))
            self.set_piece(self.rows - 1, self.rows - (i + 1), chess_piece.Piece('W', self.pieces[i + 1], i + 4))
            i += 1

        # Queen
        self.set_piece(0, 3, chess_piece.Piece('B', self.pieces[4], 1))
        self.set_piece(self.rows - 1, 3, chess_piece.Piece('W', self.pieces[4], 0))

        # King
        self.set_piece(0, 4, chess_piece.Piece('B', self.pieces[5], 1, True))
        self.set_piece(self.rows - 1, 4, chess_piece.Piece('W', self.pieces[5], 0, True))

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
                if temp_piece is not None and temp_piece.team != king_piece.team:
                    if list(filter(lambda pos: pos == [r1, c1], self.compute_valid_moves(row, col, temp_piece.team, False))):
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
                temp_state.set_piece(r1, c1 - 1, temp_state.get_piece(r1, self.rows - 1))
                temp_state.set_piece(r1, self.rows - 1, None)
            elif move[1] - c1 == 2:
                # Queen side
                temp_state.set_piece(r1, c1 + 1, temp_state.get_piece(r1, 0))
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
                if not piece.moved and self.get_piece(r1 + (direction * 2), c1) is None and self:
                    valid_moves.append([r1 + (direction * 2), c1])

            top_right = self.get_piece(r1 + (direction * 1), c1 + 1)
            top_left = self.get_piece(r1 + (direction * 1), c1 - 1)

            if top_right is not None:
                if top_right.team != piece.team:
                    valid_moves.append([r1 + (direction * 1), c1 + 1])
                    self.get_piece(r1 + (direction * 1), c1 + 1).attacked_by.append([r1, c1])
                else:
                    self.get_piece(r1 + (direction * 1), c1 + 1).defended_by.append([r1, c1])
            if top_left is not None:
                if top_left.team != piece.team:
                    valid_moves.append([r1 + (direction * 1), c1 - 1])
                    self.get_piece(r1 + (direction * 1), c1 - 1).attacked_by.append([r1, c1])
                else:
                    self.get_piece(r1 + (direction * 1), c1 - 1).defended_by.append([r1, c1])

        if piece.piece_type == 'R' or piece.piece_type == 'Q':
            signs = [[1, 0], [0, 1], [-1, 0], [0, -1]]

            for sign in signs:
                i = 1
                while self.in_range(r1 + (sign[0] * i), c1 + (sign[1] * i)) and self.get_piece(r1 + (sign[0] * i), c1 + (sign[1] * i)) is None:
                    valid_moves.append([r1 + (sign[0] * i), c1 + (sign[1] * i)])
                    i += 1
                if self.in_range(r1 + (sign[0] * i), c1 + (sign[1] * i)):
                    if self.get_piece(r1 + (sign[0] * i), c1 + (sign[1] * i)).team != piece.team:
                        valid_moves.append([r1 + (sign[0] * i), c1 + (sign[1] * i)])
                        self.get_piece(r1 + (sign[0] * i), c1 + (sign[1] * i)).attacked_by.append([r1, c1])
                    else:
                        # pass
                        self.get_piece(r1 + (sign[0] * i), c1 + (sign[1] * i)).defended_by.append([r1, c1])

        if piece.piece_type == 'N':
            signs = [[1, 1], [1, -1], [-1, 1], [-1, -1]]

            for sign in signs:
                if self.in_range(r1 + (sign[0] * 1), c1 + (sign[1] * 2)):
                    if self.get_piece(r1 + (sign[0] * 1), c1 + (sign[1] * 2)) is None:
                        valid_moves.append([r1 + (sign[0] * 1), c1 + (sign[1] * 2)])
                    elif self.get_piece(r1 + (sign[0] * 1), c1 + (sign[1] * 2)).team != piece.team:
                        valid_moves.append([r1 + (sign[0] * 1), c1 + (sign[1] * 2)])
                        self.get_piece(r1 + (sign[0] * 1), c1 + (sign[1] * 2)).attacked_by.append([r1, c1])
                    else:
                        self.get_piece(r1 + (sign[0] * 1), c1 + (sign[1] * 2)).defended_by.append([r1, c1])
                if self.in_range(r1 + (sign[0] * 2), c1 + (sign[1] * 1)):
                    if self.get_piece(r1 + (sign[0] * 2), c1 + (sign[1] * 1)) is None:
                        valid_moves.append([r1 + (sign[0] * 2), c1 + (sign[1] * 1)])
                    elif self.get_piece(r1 + (sign[0] * 2), c1 + (sign[1] * 1)).team != piece.team:
                        valid_moves.append([r1 + (sign[0] * 2), c1 + (sign[1] * 1)])
                        self.get_piece(r1 + (sign[0] * 2), c1 + (sign[1] * 1)).attacked_by.append([r1, c1])
                    else:
                        self.get_piece(r1 + (sign[0] * 2), c1 + (sign[1] * 1)).defended_by.append([r1, c1])

        if piece.piece_type == 'B' or piece.piece_type == 'Q':
            signs = [[1, 1], [1, -1], [-1, 1], [-1, -1]]

            for sign in signs:
                i = 1
                while self.in_range(r1 + (sign[0] * i), c1 + (sign[1] * i)) and self.get_piece(r1 + (sign[0] * i), c1 + (sign[1] * i)) is None:
                    valid_moves.append([r1 + (sign[0] * i), c1 + (sign[1] * i)])
                    i += 1

                if self.in_range(r1 + (sign[0] * i), c1 + (sign[1] * i)):
                    if self.get_piece(r1 + (sign[0] * i), c1 + (sign[1] * i)).team != piece.team:
                        valid_moves.append([r1 + (sign[0] * i), c1 + (sign[1] * i)])
                        self.get_piece(r1 + (sign[0] * i), c1 + (sign[1] * i)).attacked_by.append([r1, c1])
                    else:
                        self.get_piece(r1 + (sign[0] * i), c1 + (sign[1] * i)).defended_by.append([r1, c1])

        if piece.piece_type == 'K':
            # Disallow moves that result in check
            for row in range(r1 - 1, r1 + 2):
                for col in range(c1 - 1, c1 + 2):
                    if self.in_range(row, col) and (self.get_piece(row, col) is None or self.get_piece(row, col).team != piece.team):
                        valid_moves.append([row, col])

            # Castling
            if piece.moved:
                self.can_castle[team] = [False, False]
            else:
                # King side
                self.can_castle[team] = [True, True]
                for col in range(c1 + 1, self.rows - 1):
                    if self.get_piece(r1, col) is not None:
                        self.can_castle[team][1] = False
                        pass
                far_right_piece = self.get_piece(r1, self.rows - 1)
                self.can_castle[team][1] = self.can_castle[team][1] and far_right_piece is not None and far_right_piece.piece_type == 'R' and far_right_piece.team == team and not far_right_piece.moved
                # Queen side
                for col in range(1, c1):
                    if self.get_piece(r1, col) is not None:
                        self.can_castle[team][0] = False
                        pass
                far_left_piece = self.get_piece(r1, 0)
                self.can_castle[team][0] = self.can_castle[team][0] and far_left_piece is not None and far_left_piece.piece_type == 'R' and far_left_piece.team == team and not far_left_piece.moved

                if self.can_castle[team][1]:
                    valid_moves.append([r1, c1 + 2])
                if self.can_castle[team][0]:
                    valid_moves.append([r1, c1 - 2])

        if filter_check_moves:
            valid_moves = list(filter(lambda move: self.in_range(move[0], move[1]) and not self.results_in_check(r1, c1, move, not filter_check_moves),valid_moves))

        return valid_moves

    def evaluate_score(self, team):
        # Three stage evaluation:
        # Stage 1: material and pawn-king structure
        # Stage 2: dynamic piece-square tables
        # Stage 3: mobility and board control (no of available moves high is valuable)

        # TODO: Passed pawns, King Safety and Pawn Structure.
        # TODO: pawn rams, pawn levers, duo trio quart

        opposition = self.colors[(self.colors.index(team)+1) % 2]

        if self.check_checkmate(opposition):
            return float('inf')

        if self.check_checkmate(team):
            return float('-inf')

        further_moves = []
        self.search_game_tree(team, 1, further_moves)
        mobility_score = len(further_moves) * 3

        material_balance = 0
        positional_balance = 0
        bishop_count = 0
        defended_pawns_count = 0
        other_defended_pieces_count = 0

        # If black piece table needs to be vertically reflected and horizontally reflected

        for row in range(self.rows):
            for col in range(self.rows):
                piece = self.get_piece(row, col)
                color_based_access = [[row, col], [self.rows - 1 - row, self.rows - 1 - col]] if team == 'W' else [[self.rows - 1 - row, self.rows - 1 - col], [row, col]]
                if piece is None:
                    pass
                elif piece.team == team:
                    attacked_by = []
                    piece.attacked_by = list(filter(lambda pos : attacked_by.append(pos) if pos not in attacked_by else pos, piece.attacked_by))
                    piece.attacked_by = attacked_by

                    material_balance += tables.centipawn_piece_dict[piece.piece_type]
                    positional_balance += tables.centipawn_position_dict[piece.piece_type][color_based_access[0][0]][color_based_access[0][1]]
                    proportion = tables.centipawn_piece_dict[piece.piece_type]/tables.centipawn_piece_dict['Q'] if piece.piece_type != 'K' else 0.5
                    if piece.piece_type == 'B':
                        other_defended_pieces_count += len(piece.defended_by)*proportion
                        other_defended_pieces_count -= len(piece.attacked_by)*proportion
                        bishop_count += 1
                    elif piece.piece_type == 'P':
                        defended_pawns_count += len(piece.defended_by)
                    else:
                        other_defended_pieces_count += len(piece.defended_by)*proportion
                        other_defended_pieces_count -= len(piece.attacked_by)*proportion
                    if 2 < col < 5:
                        if 2 < row < 5:
                            positional_balance += 35
                        elif 1 < row < 6:
                            positional_balance += 10
                    if piece.castled is not None and piece.castled:
                        positional_balance += 300
                else:
                    attacked_by = []
                    piece.attacked_by = list(filter(lambda pos: attacked_by.append(pos) if pos not in attacked_by else pos, piece.attacked_by))
                    piece.attacked_by = attacked_by
                    material_balance -= tables.centipawn_piece_dict[piece.piece_type]
                    positional_balance -= tables.centipawn_position_dict[piece.piece_type][color_based_access[1][0]][color_based_access[1][1]]
                    proportion = tables.centipawn_piece_dict[piece.piece_type]/tables.centipawn_piece_dict['Q'] if piece.piece_type != 'K' else 0.5
                    if piece.piece_type == 'B':
                        bishop_count -= 1
                        other_defended_pieces_count -= len(piece.defended_by)*proportion
                        other_defended_pieces_count += len(piece.attacked_by)*proportion
                    elif piece.piece_type == 'P':
                        defended_pawns_count -= len(piece.defended_by)
                    else:
                        other_defended_pieces_count -= len(piece.defended_by)*proportion
                        other_defended_pieces_count += len(piece.attacked_by)*proportion
                    if 2 < col < 5:
                        if 2 < row < 5:
                            positional_balance -= 35
                        elif 1 < row < 6:
                            positional_balance -= 10
                    if piece.castled is not None and piece.castled:
                        positional_balance -= 300

        if bishop_count == 2 or bishop_count == -2:
            material_balance += (bishop_count * 25)

        # When to avoid, and when to play, for draw

        if self.fifty_move_count > 46:
            if len(self.dead_pieces[team]) < len(self.dead_pieces[opposition]):
                positional_balance -= 2000
            else:
                positional_balance += 2000

        # Go for check towards end:

        dead_pieces = len(self.dead_pieces['W']) + len(self.dead_pieces['B'])

        if dead_pieces > 14 and self.position_in_check(opposition):
            positional_balance += 8000

        scale = 500 if dead_pieces > 12 else 800 - (dead_pieces*8) - (self.move_count*2)

        return material_balance + positional_balance + mobility_score + (defended_pawns_count * 5) + (other_defended_pieces_count * scale)

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
        opposition_team = self.colors[(self.colors.index(team) + 1) % 2]

        if depth == 0:
            return self

        boards = []
        self.search_game_tree(team, 1, boards)
        max_value = float('-inf')
        max_board = None

        if maximiser:
            for board in boards:
                minimax_board = board.minimax(depth - 1, opposition_team, not maximiser, alpha, beta)
                board_score = minimax_board.evaluate_score(team)
                if board_score > max_value:
                    max_value = board_score
                    max_board = board
                alpha = max(alpha, max_value)
                if beta <= alpha:
                    break
        else:
            for board in boards:
                minimax_board = board.minimax(depth - 1, opposition_team, not maximiser, alpha, beta)
                board_score = minimax_board.evaluate_score(team)
                if board_score > max_value:
                    max_value = board_score
                    max_board = minimax_board
                beta = min(beta, max_value)
                if beta <= alpha:
                    break

        return max_board

    def display_dead_pieces(self):
        print(list(map(lambda piece: piece.display_text, self.dead_pieces['W'])))
        print(list(map(lambda piece: piece.display_text, self.dead_pieces['B'])))

    # Prints to terminal a representation of board if board.svg unviewable
    def display_board(self):
        print('\n')
        for i in range(self.rows):
            row = map(lambda pos: pos if pos[1] is None else [pos[0], pos[1].display_text], self.grid[i])
            print(*row)
        print('\n')

    def export_board_string(self):
        board_string = ""
        for row in range(self.rows):
            empty_count = 0
            for col in range(self.rows):
                piece = self.get_piece(row, col)
                if piece is None:
                    empty_count += 1
                else:
                    if empty_count != 0:
                        board_string += str(empty_count)
                        empty_count = 0
                    board_string += piece.piece_type.lower() if piece.team == 'B' else piece.piece_type

                if col == self.rows - 1 and empty_count != 0:
                    board_string += str(empty_count)
                    empty_count = 0
            if row < self.rows - 1:
                board_string += "/"

        print(board_string)
        return board_string

    def update_board_svg(self, filename="board.svg"):
        board = chess.Board(self.export_board_string())
        svg_text = chess.svg.board(board)
        svg_file = open(filename, "w")
        svg_file.write(svg_text)
        svg_file.close()

    def import_board(self, board_string):
        board_string = board_string.split('/')
        for row in range(len(board_string)):
            row_string = list(board_string[row])
            self.import_board_row(row_string, row)

    def import_board_row(self, row_string, row, col=0):
        # Pre: assumes board_string well formed.
        if not row_string:
            return
        if row_string[0].isdigit():
            spaces = int(row_string[0])
            for i in range(spaces):
                self.set_piece(row, col + i, None)
            col += spaces
        if row_string[0].islower():
            self.set_piece(row, col, chess_piece.Piece('B', row_string[0].upper(), 3, False, True))
            col += 1
        if row_string[0].isupper():
            self.set_piece(row, col, chess_piece.Piece('W', row_string[0], 3, False, True))
            col += 1
        self.import_board_row([row_string[i] for i in range(1, len(row_string))], row, col)


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
                # differences.append(['X', (src[0], src[1]), (row, col)])

    return differences


if __name__ == "__main__":
    board = Board()
    board.setup_pieces()

    board.update_board_svg()

    # board.import_board("rnbqkbnr/ppp2ppp/3pp3/8/8/8/PPPPPPPP/RNBQKBNR")
    # board.update_board_svg()

    i = 0
    while not board.check_checkmate(board.colors[i % 2]) and board.fifty_move_count < 50:

        next_board = board.minimax(2, board.colors[i % 2], True)

        if next_board is None:
            print('Stalemate')
            break

        # differences = differences_between_boards(board, next_board)
        # print(differences)
        # print(list(map(lambda pos: next_board.get_piece(pos[1][0], pos[1][1]).defended_by if next_board.get_piece(pos[1][0], pos[1][1]) is not None else [], differences)))
        # print(list(map(lambda pos: next_board.get_piece(pos[1][0], pos[1][1]).attacked_by if next_board.get_piece(pos[1][0], pos[1][1]) is not None else [], differences)))

        # next_board.display_dead_pieces()
        print(board.colors[i % 2] + "'s move. Move " + str(i + 1) + ".")
        board.update_board_svg("oldboard.svg")
        next_board.update_board_svg()

        board = next_board
        i += 1

    if board.fifty_move_count >= 50:
        print('Draw by 50 move rule')
    else:
        print(board.colors[(i + 1) % 2] + " wins!")

    print('Done')
