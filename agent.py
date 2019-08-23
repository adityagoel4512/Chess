import piecesquaretables as tables


class Agent:

    def __init__(self, team, hyperparameters={}):
        self.team = team
        if not hyperparameters:
            self.hyperparameters = {'mobility': 3, 'safespaces': 250, 'otherdefendedcount': 20, 'pawndefendedcount': 65,
                                    'netvalue': 0.1, 'scaleinitial': 4000, 'check': 500, 'centreposition': 3,
                                    'draw': 10000, 'castling': 900, 'stronglyprotected': 25,
                                    'weaklyprotectedattacked': 60000, 'deadpiecescalefactor': 15, 'movescalefactor': 13,
                                    'scalemin': 2500, 'materialbalance': 1800000, 'positionalbalance': 1,
                                    'relativepiecevalues': tables.centipawn_piece_dict, 'kingthreeshield': 400,
                                    'flankprotectionking': 125}
        else:
            self.hyperparameters = hyperparameters

    def evaluate_score(self, board, team):
        # Three stage evaluation:
        # Stage 1: material and pawn-king structure
        # Stage 2: dynamic piece-square tables
        # Stage 3: mobility and board control (no of available moves high is valuable)
        # TODO: Passed pawns, King Safety and Pawn St   ructure.
        # TODO: pawn rams, pawn levers, duo trio quart

        opposition = board.colors[(board.colors.index(team) + 1) % 2]

        if board.check_checkmate(opposition):
            return float('inf')
        further_moves = []
        board.search_game_tree(team, 1, further_moves)
        mobility_score = len(further_moves) * self.hyperparameters['mobility']

        material_balance, positional_balance, defended_pawns_count, other_defended_pieces_count, net_value_defence_attack = 0, 0, 0, 0, 0
        bishop_count = {team: 0, opposition: 0}

        # If black piece table needs to be vertically reflected and horizontally reflected
        direction = 1 if team == 'W' else 1
        # Stockfish tactic to improve opening game by counting safe spaces in center of board
        safe_spaces = 0
        # Stockfish tactic to improve piece protection: either protected by pawn, or by two while we protect with one
        strongly_protected = 0
        weakly_protected_under_attack = 0
        king_value = self.hyperparameters['relativepiecevalues']['K'] + 300

        for row in range(board.rows):
            for col in range(board.rows):
                piece = board.get_piece(row, col)
                color_based_access = [[row, col], [board.rows - 1 - row, board.rows - 1 - col]] if team == 'W' else [[board.rows - 1 - row, board.rows - 1 - col], [row, col]]
                if piece is None:
                    pass
                else:
                    piece_material_balance, piece_positional_balance, piece_defended_pawns_count, piece_other_defended_pieces_count, piece_net_value_defence_attack = 0, 0, 0, 0, 0
                    piece_material_balance += self.hyperparameters['relativepiecevalues'][piece.piece_type]
                    piece_positional_balance += tables.centipawn_position_dict[piece.piece_type][color_based_access[0][0]][color_based_access[0][1]]
                    proportion = self.hyperparameters['relativepiecevalues'][piece.piece_type]*2 / self.hyperparameters['relativepiecevalues']['Q'] if piece.piece_type != 'K' else 0.01

                    if piece.piece_type == 'B':
                        piece_other_defended_pieces_count += len(piece.defended_by) * proportion
                        piece_other_defended_pieces_count -= len(piece.attacked_by) * proportion
                        bishop_count[piece.team] += 1
                        if bishop_count[piece.team] == 2:
                            material_balance += 60
                    elif piece.piece_type == 'R':
                        piece_other_defended_pieces_count += len(piece.defended_by) * proportion
                        piece_other_defended_pieces_count -= len(piece.attacked_by) * proportion
                        for i in range(row, board.rows):
                            if board.get_piece(i, col) is None:
                                piece_positional_balance += 50

                    elif piece.piece_type == 'P':
                        piece_defended_pawns_count += len(piece.defended_by)
                    elif piece.piece_type == 'K':
                        # King protection
                        flank_protection = [False, False]

                        for i in range(col, board.rows):
                            temp_piece = board.get_piece(row, i)
                            if board.get_piece(row, i) is not None and temp_piece.team == team:
                                flank_protection[1] = True
                                break
                        for i in range(0, col):
                            temp_piece = board.get_piece(row, i)
                            if board.get_piece(row, i) is not None and temp_piece.team == team:
                                flank_protection[0] = True
                                break

                        piece_positional_balance += len(list(filter(lambda protected: protected, flank_protection))) * self.hyperparameters['flankprotectionking']

                        front_three_pieces = [board.get_piece(direction * 1 + row, col - 1),
                                              board.get_piece(direction * 1 + row, col),
                                              board.get_piece(direction * 1 + row, col + 1)]

                        piece_positional_balance += len(list(filter(lambda p: p is not None and p.team == team, front_three_pieces))) * self.hyperparameters['kingthreeshield']
                        piece_other_defended_pieces_count += len(piece.defended_by) * proportion
                        piece_other_defended_pieces_count -= len(piece.attacked_by) * proportion

                    else:
                        piece_other_defended_pieces_count += len(piece.defended_by) * proportion
                        piece_other_defended_pieces_count -= len(piece.attacked_by) * proportion

                    factor = -1 if piece.team != team else 1

                    if piece.attacked_by:
                        attacked_by = []
                        piece.attacked_by = list(filter(lambda pos: attacked_by.append(pos) if pos not in attacked_by else pos and board.get_piece(pos[0], pos[1]) is not None, piece.attacked_by))
                        piece.attacked_by = attacked_by

                        if list(filter(lambda pos: board.get_piece(pos[0], pos[1]).piece_type != 'P', piece.attacked_by)) and not (list(filter(lambda pos: board.get_piece(pos[0], pos[1]) is not None and board.get_piece(pos[0], pos[1]).piece_type == 'P', piece.defended_by))
                                 or (len(piece.defended_by) == 2 and piece is not None and not list(filter(lambda pos: len(board.get_piece(pos[0], pos[1]).defended_by) >= 2, piece.attacked_by)))):
                            weakly_protected_under_attack += factor

                        for pos in piece.attacked_by:
                            piece_net_value_defence_attack -= king_value - (self.hyperparameters['materialbalance'] * self.hyperparameters['relativepiecevalues'][board.get_piece(pos[0], pos[1]).piece_type])

                        piece.attacked_by.clear()

                    if piece.defended_by:
                        defended_by = []
                        piece.defended_by = list(filter(lambda pos: defended_by.append(pos) if pos not in defended_by else pos and board.get_piece(pos[0], pos[1]) is not None, piece.defended_by))
                        piece.defended_by = defended_by

                        if list(filter(lambda pos: board.get_piece(pos[0], pos[1]) is not None and board.get_piece(pos[0], pos[1]).piece_type == 'P', piece.defended_by)):
                            strongly_protected += factor
                        elif len(piece.defended_by) == 2 and piece is not None and not list(filter(lambda pos: len(board.get_piece(pos[0], pos[1]).defended_by) >= 2, piece.attacked_by)):
                            strongly_protected += factor

                        for pos in piece.attacked_by:
                            piece_net_value_defence_attack += king_value - (self.hyperparameters['materialbalance'] * self.hyperparameters['relativepiecevalues'][board.get_piece(pos[0], pos[1]).piece_type])

                        piece.defended_by.clear()

                    valid_moves = board.compute_valid_moves(row, col, piece.team, True)

                    if 2 < row < 5 and 2 < col < 5:
                        safe_spaces += self.hyperparameters['centreposition'] * factor

                    safe_spaces += 1 * len(list(filter(lambda pos: 2 < pos[0] < 5 and 1 < pos[1] < 6, valid_moves))) * factor

                    if piece.castled is not None and piece.castled:
                        piece_positional_balance += self.hyperparameters['castling'] * factor

                    material_balance += piece_material_balance * factor
                    positional_balance += (piece_positional_balance * factor) + (safe_spaces * self.hyperparameters['safespaces']) + (strongly_protected * self.hyperparameters['stronglyprotected']) - (weakly_protected_under_attack * self.hyperparameters['weaklyprotectedattacked'])

                    other_defended_pieces_count += piece_other_defended_pieces_count * factor
                    defended_pawns_count += piece_defended_pawns_count * factor
                    net_value_defence_attack += piece_net_value_defence_attack * factor

        # When to avoid, and when to play, for draw

        if board.fifty_move_count > 30:
            positional_balance -= 9999999999999999

        # if board.fifty_move_count > 46:
        #     if len(board.dead_pieces[team]) < len(board.dead_pieces[opposition]):
        #         positional_balance -= self.hyperparameters['draw']
        #     else:
        #         positional_balance += self.hyperparameters['draw']

        # Go for check, especially towards end:

        dead_pieces = len(board.dead_pieces['W']) + len(board.dead_pieces['B'])

        if board.position_in_check(opposition):
            positional_balance += self.hyperparameters['check'] * dead_pieces
        if board.position_in_check(team):
            positional_balance -= self.hyperparameters['check'] * dead_pieces

        scale = self.hyperparameters['scalemin'] if dead_pieces > 12 else self.hyperparameters['scaleinitial'] - (dead_pieces * self.hyperparameters['deadpiecescalefactor']) - (board.move_count * self.hyperparameters['movescalefactor'])

        return self.hyperparameters['materialbalance'] * material_balance + self.hyperparameters['positionalbalance'] * positional_balance + mobility_score + (self.hyperparameters['pawndefendedcount'] * defended_pawns_count * scale) + (self.hyperparameters['otherdefendedcount'] * other_defended_pieces_count * scale) + (net_value_defence_attack * self.hyperparameters['netvalue'])