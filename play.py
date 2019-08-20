import sys
import datetime
import board as chessboard
import functools

ALPHA_OFFSET = ord('a')


def engine_play_engine(minimax_depth):
    board = chessboard.Board()
    board.setup_pieces()
    board.update_board_svg("board" + str(board.move_count) + ".svg")

    while not board.check_checkmate(board.colors[(board.move_count-1) % 2]) and board.fifty_move_count < 50:

        board = board.minimax(minimax_depth, board.colors[board.move_count % 2], True, board)

        if board is None:
            print('Draw by stalemate')
            break

        print(board.colors[(board.move_count-1) % 2] + "'s move. Move " + str(board.move_count) + " at " + str(datetime.datetime.now()) + ".")
        board.update_board_svg("board" + str(board.move_count) + ".svg")
        board.clear_all_defending_attacking()

    if board.fifty_move_count >= 50:
        print('Draw by 50 move rule')
    else:
        print(board.colors[board.move_count% 2] + " wins!")


def human_play_engine(minimax_depth, team='W'):
    board = chessboard.Board()
    board.setup_pieces()

    print('You are ' + team)

    board.update_board_svg("current_state.svg")

    player = board.colors.index(team)
    rough_eval_table = {}

    while not board.check_checkmate(board.colors[(board.move_count-1) % 2]) and board.fifty_move_count < 50:

        old_board_string = board.export_board_string()
        # Key format: boardstring-castlewhite-castleblack-50movecount>40
        # eg: "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNRTFT"

        if board.move_count % 2 == player:
            c1, r1, c2, r2 = list(input('Enter move in format "d2d4" ([src][dst])'))

            row1, col1, row2, col2 = board.rows-int(r1), ord(c1)-ALPHA_OFFSET, board.rows-int(r2), ord(c2)-ALPHA_OFFSET

            while not board.move_piece(row1, col1, row2, col2, team, True):
                print('Invalid Move')
                c1, r1, c2, r2 = list(input('Enter move in format "d2d4" ([src][dst])'))
                row1, col1, row2, col2 = board.rows - int(r1), ord(c1) - ALPHA_OFFSET, board.rows - int(r2), ord(c2) - ALPHA_OFFSET
        else:
            board = board.minimax(minimax_depth, board.colors[board.move_count % 2], True, board)
            print(chessboard.Board.evaluate_score.cache_info())

        # print(len(transposition_table))
        if board is None:
            print('Draw by stalemate')
            break

        print(board.colors[(board.move_count-1) % 2] + "'s move. Move " + str(board.move_count) + " at " + str(datetime.datetime.now()) + ".")
        board.update_board_svg("previous_state.svg", old_board_string)
        board.update_board_svg("current_state.svg")
        board.clear_all_defending_attacking()

    if board.fifty_move_count >= 50:
        print('Draw by 50 move rule')
    else:
        print(board.colors[board.move_count % 2] + " wins!")


if __name__ == "__main__":

    player = len(sys.argv)
    minimax_depth = int(sys.argv[1])

    if player == 3:
        team = str(sys.argv[2])
        human_play_engine(minimax_depth, team)
    elif player == 2:
        engine_play_engine(minimax_depth)
    else:
        print("See program spec for how to structure command line arguments")

    print('Done')