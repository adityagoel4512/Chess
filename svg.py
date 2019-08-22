import chess
import chess.svg
from piece import Piece


def update_board_svg(self, filename="board.svg", board_string=None):
    board = chess.Board(self.board_text if board_string is None else board_string)
    svg_text = chess.svg.board(board)
    svg_file = open(filename, "w")
    svg_file.write(svg_text)
    svg_file.close()


def display_dead_pieces(self):
    print(list(map(lambda piece: piece.display_text, self.dead_pieces['W'])))
    print(list(map(lambda piece: piece.display_text, self.dead_pieces['B'])))


def display_board(self):
    print('\n')
    for i in range(self.rows):
        row = map(lambda pos: pos if pos[1] is None else [pos[0], pos[1].display_text], self.grid[i])
        print(*row)
    print('\n')


def import_board(self, board_string):
    # Pre: assumes board_string well formed.
    # Format is the same as the Python Chess library.

    def import_board_row(self, row_string, row, col=0):
        if not row_string:
            return
        if row_string[0].isdigit():
            spaces = int(row_string[0])
            for i in range(spaces):
                self.set_piece(row, col + i, None)
            col += spaces
        if row_string[0].islower():
            self.set_piece(row, col, Piece('B', row_string[0].upper(), 3, False, True))
            col += 1
        if row_string[0].isupper():
            self.set_piece(row, col, Piece('W', row_string[0], 3, False, True))
            col += 1
        self.import_board_row([row_string[i] for i in range(1, len(row_string))], row, col)

    board_string = board_string.split('/')
    for row in range(len(board_string)):
        row_string = list(board_string[row])
        import_board_row(self, row_string, row)

