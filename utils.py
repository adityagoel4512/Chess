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

    return differences
