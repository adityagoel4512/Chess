import sys
import datetime
from board import Board
import functools
from svg import update_board_svg

ALPHA_OFFSET = ord('a')


def engine_play_engine(minimax_depth):
    board = Board()
    board.setup_pieces()
    update_board_svg(board, "board" + str(board.move_count) + ".svg")

    while not board.check_checkmate(board.colors[(board.move_count-1) % 2]) and board.fifty_move_count < 50:

        board = board.minimax(minimax_depth, board.colors[board.move_count % 2], True, board)

        if board is None:
            print('Draw by stalemate')
            break

        # print(Board.compute_valid_moves.cache_info())
        print(board.colors[(board.move_count-1) % 2] + "'s move. Move " + str(board.move_count) + " at " + str(datetime.datetime.now()) + ".")
        update_board_svg(board, "board" + str(board.move_count) + ".svg")
        board.clear_all_defending_attacking()

    if board.fifty_move_count >= 50:
        print('Draw by 50 move rule')
    else:
        print(board.colors[board.move_count% 2] + " wins!")


def human_play_engine(minimax_depth, team='W'):
    board = Board()
    board.setup_pieces()

    print('You are ' + team)

    update_board_svg(board, "current_state.svg")

    player = board.colors.index(team)

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
            # print(Board.compute_valid_moves.cache_info())

        if board is None:
            print('Draw by stalemate')
            break

        print(board.export_board_string())
        print(board.colors[(board.move_count-1) % 2] + "'s move. Move " + str(board.move_count) + " at " + str(datetime.datetime.now()) + ".")
        update_board_svg(board, "previous_state.svg", old_board_string)
        update_board_svg(board, "current_state.svg")
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