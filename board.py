from piece import Piece
from agent import Agent
import functools

# TODO: Future Tasks
# Instead of expensive deepcopying and moving, utilising zobrist hashing to make and unmake moves


class Board:

    grid = []
    rows = 8
    colors = ['W', 'B']
    pieces = ['P', 'R', 'N', 'B', 'Q', 'K']

    def __init__(self, grid=None, king_pos={'W': [7, 4], 'B': [0, 4]}, move_count=0,
                 can_castle={'W': [False, False], 'B': [False, False]},
                 dead_pieces={'W': [], 'B': []},
                 fifty_move_count=0,
                 promotion_occured={'W': False, 'B': False}, board_string=None):

        self.king_pos = king_pos
        self.move_count = move_count
        # King side 2nd element, Queen side 1st element.
        self.can_castle = can_castle
        self.dead_pieces = dead_pieces
        self.fifty_move_count = fifty_move_count
        self.promotion_occured = promotion_occured
        self.agents = {'W': Agent('W'),
                       'B': Agent('B', {'mobility': 4, 'safespaces': 350, 'otherdefendedcount': 35,
                                        'pawndefendedcount': 60, 'netvalue': 15, 'scaleinitial': 3400, 'check': 1800,
                                        'centreposition': 9, 'draw': 1500, 'castling': 600, 'stronglyprotected': 40,
                                        'weaklyprotectedattacked': 850000, 'deadpiecescalefactor': 10,
                                        'movescalefactor': 30, 'scalemin': 2750, 'materialbalance': 10000010,
                                        'positionalbalance': 1, 'relativepiecevalues':
                                        {'P': 1, 'N': 3, 'B': 5, 'R': 5.5, 'Q': 21, 'K': 1000000},
                                        'kingthreeshield': 600, 'flankprotectionking': 125})}
        if grid is None:
            for i in range(self.rows):
                self.grid.append([])
                for j in range(self.rows):
                    self.grid[i].append([self.colors[(i + j) % 2], None])
        else:
            self.grid = grid
        if board_string is None:
            self.recompute_board_string()
        else:
            # Print board string if you want to reconstruct this board state at a separate point with import_board.
            # Only encodes the way the board is represented and not advanced features for chess engine
            # Assume white is next to play
            self.board_text = board_string

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

        copy_king_pos = {'W': list(map(lambda pos: pos, self.king_pos['W'])),
                         'B': list(map(lambda pos: pos, self.king_pos['B']))}
        copy_can_castle = {'W': list(map(lambda castle: castle, self.can_castle['W'])),
                           'B': list(map(lambda castle: castle, self.can_castle['B']))}
        copy_dead_pieces = {'W': list(map(lambda piece: piece.__copy__(), self.dead_pieces['W'])),
                            'B': list(map(lambda piece: piece.__copy__(), self.dead_pieces['B']))}
        copy_fifty_move_count = self.fifty_move_count
        copy_move_count = self.move_count
        copy_promotion_occured = {'W': self.promotion_occured['W'], 'B': self.promotion_occured['B']}
        return Board(copy_grid, copy_king_pos, copy_move_count, copy_can_castle, copy_dead_pieces, copy_fifty_move_count, copy_promotion_occured, self.board_text)

    def __hash__(self):
        team_to_move = self.colors[(self.move_count-1)%2]
        white_castle = str(self.can_castle['W'][0] and self.can_castle['W'][1])
        black_castle = str(self.can_castle['B'][0] and self.can_castle['B'][1])
        near_fifty_move_draw = 'T' if self.fifty_move_count >= 40 else 'F'
        team_promoted = str(self.promotion_occured[team_to_move])
        return hash(''.join((self.board_text, white_castle, black_castle, near_fifty_move_draw, team_to_move, team_promoted)))

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
            self.king_pos[piece.team] = [row, column]
        self.grid[row][column][1] = piece

    def move_piece(self, r1, c1, r2, c2, team, filter_check_moves):
        piece = self.get_piece(r1, c1)
        valid_moves = self.compute_valid_moves(r1, c1, team, filter_check_moves)

        if not [r2, c2] in valid_moves:
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
            if r2 == self.rows-1 or r2 == 0:
                # TODO: pawn promotion as part of engine decision making and not automatically choosing queen over knight
                self.set_piece(r2, c2, Piece(team, 'Q', 4))
                self.promotion_occured[team] = True

        self.move_count += 1
        piece.moved = True

        self.incremental_board_string_update(r1, c1, r2, c2, piece.piece_type if piece.team == 'W' else piece.piece_type.lower())
        return True

    def setup_pieces(self):
        for i in range(self.rows):
            self.set_piece(6, i, Piece('W', 'P', i))
            self.set_piece(1, i, Piece('B', 'P', i))

        # Rooks, Knights, Bishops
        i = 0
        while i < 3:
            self.set_piece(0, i, Piece('B', self.pieces[i + 1], i))
            self.set_piece(0, self.rows - (i + 1), Piece('B', self.pieces[i + 1], i + 4))
            self.set_piece(self.rows - 1, i, Piece('W', self.pieces[i + 1], i))
            self.set_piece(self.rows - 1, self.rows - (i + 1), Piece('W', self.pieces[i + 1], i + 4))
            i += 1

        # Queen
        self.set_piece(0, 3, Piece('B', self.pieces[4], 1))
        self.set_piece(self.rows - 1, 3, Piece('W', self.pieces[4], 0))

        # King
        self.set_piece(0, 4, Piece('B', self.pieces[5], 1, True))
        self.set_piece(self.rows - 1, 4, Piece('W', self.pieces[5], 0, True))
        self.board_text = self.recompute_board_string()

    def locate_piece(self, piece):
        assert piece is not None
        for row in range(self.rows):
            for col in range(self.rows):
                square = self.get_piece(row, col)
                if square is not None and piece.id == square.id and square.display_text == piece.display_text:
                    return [row, col]
        return [-1, -1]

    def position_in_check(self, side):
        r1 = self.king_pos[side][0]
        c1 = self.king_pos[side][1]
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
        king_piece = self.get_piece(self.king_pos[side][0], self.king_pos[side][1])
        if king_piece is None:
            return True

        if not self.position_in_check(side):
            return False
        for row in range(self.rows):
            for col in range(self.rows):
                piece = self.get_piece(row, col)
                if piece is not None and piece.team == king_piece.team:
                    moves = self.compute_valid_moves(row, col, piece.team, False)
                    for move in moves:
                        temp_state = self.__deepcopy__()
                        if temp_state.move_piece(row, col, move[0], move[1], piece.team, False):
                            if not temp_state.position_in_check(side):
                                return False
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

    # @functools.lru_cache(maxsize=64)
    def compute_valid_moves(self, r1, c1, team, filter_check_moves):
        # Filter check moves imposes recursion depth also
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
            for row in range(r1 - 1, r1 + 2):
                for col in range(c1 - 1, c1 + 2):
                    if self.in_range(row, col):
                        temp_piece = self.get_piece(row, col)
                        if temp_piece is None:
                            valid_moves.append([row, col])
                        elif temp_piece.team != piece.team:
                            valid_moves.append([row, col])
                            temp_piece.attacked_by.append([r1, c1])

            # Castling management
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
            # Disallow moves that result in check
            valid_moves = list(filter(lambda move: self.in_range(move[0], move[1]) and not self.results_in_check(r1, c1, move, not filter_check_moves), valid_moves))

        return valid_moves

    # @set_hyperparams

    def search_game_tree(self, start_team, moves, game_boards):
        if moves == 0:
            return
        opponent_team = self.colors[(self.colors.index(start_team) + 1) % 2]
        for row in range(self.rows):
            for col in range(self.rows):
                piece = self.get_piece(row, col)
                if piece is not None and piece.team == start_team:
                    valid_moves = self.compute_valid_moves(row, col, start_team, True)
                    for move in valid_moves:
                        temp_state = self.__deepcopy__()
                        temp_state.move_piece(row, col, move[0], move[1], start_team, True)
                        temp_state.clear_all_defending_attacking()
                        if moves == 1 and temp_state is not None:
                            game_boards.append(temp_state)
                        temp_state.search_game_tree(opponent_team, moves - 1, game_boards)

    def make_move(self, depth, team, maximiser, original_board):
        agent = self.agents[team]

        def minimax(self, depth, team, maximiser, original_board, alpha=float('-inf'), beta=float('inf'), shallow_move_ordering=False, quiescent=False):
            if self is None:
                return self
            opposition_team = self.colors[(self.colors.index(team) + 1) % 2]
            if depth == 0:
                # TODO: Quiescent search to remove horizon effect:
                # include, winning captures, pawn promotion
                # Q-searches are usually not depth-limited, and instead rely on the tree terminating. Trees will
                # always terminate (usually reasonably quickly) since the number of possible captures are usually
                # limited, and tend to decrease as captures are made.
                if not quiescent and (len(self.dead_pieces[opposition_team]) > len(original_board.dead_pieces[opposition_team]) or self.promotion_occured[team]):
                    # Pieces have been captured
                    # Quiescent search of just one further ply for now
                    return minimax(self, 1, opposition_team, not maximiser, self, alpha, beta, shallow_move_ordering, True)
                return self

                # return transposition_table[parent_node_hash_key]

            boards = []
            self.search_game_tree(team, 1, boards)
            boards = list(filter(lambda b: b is not None, boards))
            max_value = float('-inf')
            max_board = None

            if shallow_move_ordering:
                boards.sort(key=lambda board: agent.evaluate_score(self, team), reverse=True)

            if maximiser:
                for board in boards:
                    minimax_board = minimax(board, depth - 1, opposition_team, False, self, alpha, beta, shallow_move_ordering, quiescent)

                    if minimax_board is not None:
                        board_score = agent.evaluate_score(minimax_board, team)
                        if board_score > max_value:
                            max_value = board_score
                            max_board = board
                        alpha = max(alpha, max_value)
                        if beta <= alpha:
                            break
            else:
                for board in boards:
                    minimax_board = minimax(board, depth - 1, opposition_team, True, self, alpha, beta, shallow_move_ordering, quiescent)

                    if minimax_board is not None:
                        board_score = agent.evaluate_score(minimax_board, team)
                        if board_score > max_value:
                            max_value = board_score
                            max_board = minimax_board
                        beta = min(beta, max_value)
                        if beta <= alpha:
                            break

            return max_board

        return minimax(self, depth, team, maximiser, original_board)

    def clear_all_defending_attacking(self):
        for row in range(self.rows):
            for col in range(self.rows):
                piece = self.get_piece(row, col)
                if piece is not None:
                    piece.attacked_by.clear()
                    piece.defended_by.clear()

    def recompute_board_string(self):
        board_string = ''
        for row in range(self.rows):
            empty_count = 0
            for col in range(self.rows):
                piece = self.get_piece(row, col)
                if piece is None:
                    empty_count += 1
                else:
                    if empty_count != 0:
                        board_string = ''.join((board_string, str(empty_count)))
                        empty_count = 0
                    board_string = ''.join((board_string, piece.piece_type.lower())) if piece.team == 'B' else ''.join(
                        (board_string, piece.piece_type))

                if col == self.rows - 1 and empty_count != 0:
                    board_string = ''.join((board_string, str(empty_count)))
                    empty_count = 0
            if row < self.rows - 1:
                board_string = ''.join((board_string, '/'))

        return board_string

    def incremental_board_string_update(self, r1, c1, r2, c2, src_text):
        board_string_by_row = self.board_text.split('/')

        for i in range(self.rows):
            if board_string_by_row[r1][i].isdigit() and int(board_string_by_row[r1][i]) > 1:
                expansion = ''.join(['1' for j in range(int(board_string_by_row[r1][i]))])
                board_string_by_row[r1] = ''.join(
                    (board_string_by_row[r1][:i], expansion, board_string_by_row[r1][i + 1:]))

            if board_string_by_row[r2][i].isdigit() and int(board_string_by_row[r2][i]) > 1:
                expansion = ''.join(['1' for j in range(int(board_string_by_row[r2][i]))])
                board_string_by_row[r2] = ''.join(
                    (board_string_by_row[r2][:i], expansion, board_string_by_row[r2][i + 1:]))

        board_string_by_row[r2] = ''.join((board_string_by_row[r2][:c2], src_text, board_string_by_row[r2][c2 + 1:]))
        board_string_by_row[r1] = ''.join((board_string_by_row[r1][:c1], '1', board_string_by_row[r1][c1 + 1:]))

        i = 0
        while i < len(board_string_by_row[r2]):
            if board_string_by_row[r2][i] == '1':
                count = 1
                while i + count < len(board_string_by_row[r2]) and board_string_by_row[r2][i + count] == '1':
                    count += 1
                board_string_by_row[r2] = ''.join(
                    (board_string_by_row[r2][:i], str(count), board_string_by_row[r2][i + count:]))
            i += 1

        i = 0
        while i < len(board_string_by_row[r1]):
            if board_string_by_row[r1][i] == '1':
                count = 1
                while i + count < len(board_string_by_row[r1]) and board_string_by_row[r1][i + count] == '1':
                    count += 1
                board_string_by_row[r1] = ''.join(
                    (board_string_by_row[r1][:i], str(count), board_string_by_row[r1][i + count:]))
            i += 1

        self.board_text = '/'.join(board_string_by_row)





