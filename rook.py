import chess
import chess.svg
import webbrowser

if __name__ == '__main__':
    board = chess.Board('rnb1kbn1/pppppppp/7r/3q4/8/8/PPPPPPPP/RNBQKBNR')
    svg_text = chess.svg.board(board)

    svg_file = open("rook.svg", "w")
    svg_file.write(svg_text)
    svg_file.close()
    # webbrowser.open(svg_file)
