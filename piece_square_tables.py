pawn_table = [[0, 0, 0, 0, 0, 0, 0, 0],
                [50, 50, 50, 50, 50, 50, 50, 50],
                [10, 10, 20, 40, 40, 20, 10, 10],
                [5, 5, 10, 30, 30, 10, 5, 5],
                [0, 0, 7, 25, 25, 7, 0, 0],
                [-5, -5, 5, 15, 15, 5, -5, -5],
                [5, 5, 5, -20, -20, 5, 5, 5],
                [0, 0, 0, 0, 0, 0, 0, 0]]

knight_table = [[-50, -40, -30, -30, -30, -30, -40, -50],
                [-40, -20, 0, 0, 0, 0, -20, -40],
                [-30, 0, 10, 15, 15, 10, 0, -30],
                [-30, 5, 15, 20, 20, 15, 5, -30],
                [-30, 0, 15, 20, 20, 15, 0, -30],
                [-30, 5, 10, 15, 15, 10, 5, -30],
                [-40, -20, 0, 5, 5, 0, -20, -40],
                [-50, -20, -30, -30, -30, -30, -25, -50]]

bishop_table = [[-20, -10, -10, -10, -10, -10, -10, -20],
                [-10, 0, 0, 0, 0, 0, 0, -10],
                [-10, 0, 5, 10, 10, 5, 0, -10],
                [-10, 5, 5, 10, 10, 5, 5, -10],
                [-10, 0, 10, 10, 10, 10, 0, -10],
                [-10, 10, 10, 10, 10, 10, 10, -10],
                [-10, 5, 0, 0, 0, 0, 5, -10],
                [-20, -10, -10, -10, -10, -10, -10, -20]]

rook_table = [[0, 0, 0, 0, 0, 0, 0, 0],
                [5, 10, 10, 10, 10, 10, 10, 5],
                [-5, 0, 0, 0, 0, 0, 0, -5],
                [-5, 0, 0, 0, 0, 0, 0, -5],
                [-5, 0, 0, 0, 0, 0, 0, -5],
                [-5, 0, 0, 0, 0, 0, 0, -5],
                [-5, 0, 0, 0, 0, 0, 0, -5],
                [0, 0, 0, 5, 5, 0, 0, 0]]

queen_table = [[-20, -10, -10, -5, -5, -10, -10, -20],
                [-10, 0, 0, 0, 0, 0, 0, -10],
                [-10, 0, 5, 5, 5, 5, 0, -10],
                [-5, 0, 5, 5, 5, 5, 0, -5],
                [0, 0, 5, 5, 5, 5, 0, -5],
                [-10, 5, 5, 5, 5, 5, 0, -10],
                [-10, 0, 5, 0, 0, 0, 0, -10],
                [-20, -10, -10, -5, -5, -10, -10, -20]]

king_midgame_table = [[-30, -40, -40, -50, -50, -40, -40, -30],
                        [-30, -40, -40, -50, -50, -40, -40, -30],
                        [-30, -40, -40, -50, -50, -40, -40, -30],
                        [-30, -40, -40, -50, -50, -40, -40, -30],
                        [-20, -30, -30, -40, -40, -30, -30, -20],
                        [-10, -20, -20, -20, -20, -20, -20, -10],
                        [20, 20, 0, 0, 0, 0, 20, 20],
                        [20, 30, 10, 0, 0, 10, 30, 20]]

# king_endgame_table = [[-50,-40,-30,-20,-20,-30,-40,-50],
#                       [-30,-20,-10,  0,  0,-10,-20,-30],
#                       [-30,-10, 20, 30, 30, 20,-10,-30],
#                       [-30,-10, 30, 40, 40, 30,-10,-30],
#                       [-30,-10, 30, 40, 40, 30,-10,-30],
#                       [-30,-10, 20, 30, 30, 20,-10,-30],
#                       [-30,-30,  0,  0,  0,  0,-30,-30],
#                       [-50,-30,-30,-30,-30,-30,-30,-50]]

centipawn_piece_dict = {'P': 400, 'N': 2250, 'B': 4200, 'R': 4500, 'Q': 15000, 'K': 100000}
centipawn_position_dict = {'P': pawn_table, 'N': knight_table, 'B': bishop_table, 'R': rook_table,
                            'Q': queen_table, 'K': king_midgame_table}