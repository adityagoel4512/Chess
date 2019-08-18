import datetime
import board as chessboard

ALPHA_OFFSET = 97


def engine_play_engine(minimax_depth):
    board = chessboard.Board()
    board.setup_pieces()
    board.update_board_svg("board" + str(board.move_count) + ".svg")

    while not board.check_checkmate(board.colors[(board.move_count-1) % 2]) and board.fifty_move_count < 50:

        board = board.minimax(minimax_depth, board.colors[board.move_count % 2], True)

        if board is None:
            print('Stalemate')
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

    board.update_board_svg("board" + str(board.move_count) + ".svg")

    player = board.colors.index(team)
    while not board.check_checkmate(board.colors[(board.move_count-1) % 2]) and board.fifty_move_count < 50:

        if board.move_count % 2 == player:
            c1, r1, c2, r2 = list(input('Enter move in format "d2d4" ([src][dst])'))
            while not board.move_piece(board.rows-int(r1), int(ord(c1)-ALPHA_OFFSET), board.rows-int(r2), int(ord(c2)-ALPHA_OFFSET), team, True):
                print('Invalid Move')
                c1, r1, c2, r2 = list(input('Enter move in format "d2d4" ([src][dst])'))
        else:
            board = board.minimax(minimax_depth, board.colors[board.move_count % 2], True)

        if board is None:
            print('Stalemate')
            break

        print(board.colors[(board.move_count-1) % 2] + "'s move. Move " + str(board.move_count) + " at " + str(datetime.datetime.now()) + ".")
        board.update_board_svg("board" + str(board.move_count) + ".svg")
        board.clear_all_defending_attacking()

    if board.fifty_move_count >= 50:
        print('Draw by 50 move rule')
    else:
        print(board.colors[board.move_count % 2] + " wins!")


if __name__ == "__main__":
    human_play_engine(2, 'W')
    print('Done')