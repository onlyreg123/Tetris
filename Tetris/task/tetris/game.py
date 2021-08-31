import copy
import numpy as np
import re
from collections import ChainMap

patterns = {}
C_SYMBOL = '0'
C_FILL = '-'

class Piece:
    def __init__(self, piece_code):
        self.patterns = copy.deepcopy(patterns[piece_code])
        self.pattern_idx = 0


class Tetris:
    def __init__(self, rows, cols):
        self.R, self.C = rows, cols
        self.blocked_cells = np.empty(0, dtype=int)  # cells of pieces blocked
        self.left_border = list(range(0, rows * cols, cols))
        self.right_border = list(range(cols - 1, rows * cols, cols))
        self.top_border = list(range(cols))
        self.bottom_border = list(range((rows - 1) * cols, rows * cols, 1))

    def print_board(self, piece: Piece = None):
        grid = np.full(self.R * self.C, C_FILL)  # We begin with an empty grid
        if piece:
            # We add cells occupied by the actual pieces and all the blocked pieces
            grid[list(ChainMap(piece.patterns[piece.pattern_idx], self.blocked_cells))] = '0'
        else:
            grid[self.blocked_cells] = '0'

        for r in range(0, self.R):  # print the board with its pieces
            print(' '.join(grid[r * self.C: (r + 1) * self.C]))
        print()

    # We add a detected blocked piece (it's cells) into blocked_cells
    def block_cells(self, pattern):
        self.blocked_cells = np.append(pattern, self.blocked_cells)

    # Detect if we have a piece that "conflicts" with bottom row or other pieces
    def check_2block(self, piece: Piece) -> bool:
        to_block = any(elem - self.C in self.bottom_border for elem in piece.patterns[piece.pattern_idx]) or \
                   any(elem in self.blocked_cells for elem in piece.patterns[piece.pattern_idx])
        return to_block


def create_patterns():
    global patterns
    O = np.array([[4, 14, 15, 5]])
    I = np.array([[4, 14, 24, 34], [3, 4, 5, 6]])
    S = np.array([[5, 4, 14, 13], [4, 14, 15, 25]])
    Z = np.array([[4, 5, 15, 16], [5, 15, 14, 24]])
    L = np.array([[4, 14, 24, 25], [5, 15, 14, 13], [4, 5, 15, 25], [6, 5, 4, 14]])
    J = np.array([[5, 15, 25, 24], [15, 5, 4, 3], [5, 4, 14, 24], [4, 14, 15, 16]])
    T = np.array([[4, 14, 24, 15], [4, 13, 14, 15], [5, 15, 25, 14], [4, 5, 6, 15]])
    patterns = {"o": O, "i": I, "s": S, "z": Z, "t": T, "j": J, "l": L}
    return None

def main():
    create_patterns()
    piece = None
    tetris = Tetris(rows=20, cols=10)
    commands = {"down", "right", "left", "rotate", "piece", "break"}

    cmd = ""
    while cmd != "exit":
        cmd = input().lower()
        if cmd == "exit":
            break
        elif cmd in commands:  # cmd is a movement (down, left,...)
            if cmd == "piece" and piece is None:
                piece_code = input().lower()
                if piece_code in patterns:
                    piece = Piece(piece_code)
                    tetris.print_board(piece)
                    continue

            if cmd == "break":
                while True:
                    last_row_begins, last_row_ends = (tetris.R - 1) * tetris.C, tetris.R * tetris.C - 1
                    if sum(tetris.blocked_cells >= last_row_begins) == tetris.C:
                        tetris.blocked_cells += tetris.C
                        tetris.blocked_cells = np.delete(tetris.blocked_cells, tetris.blocked_cells > last_row_ends)
                    else:
                        break
                tetris.print_board(piece)
                continue

            if piece is not None:
                pattern_copy = copy.deepcopy(piece.patterns[piece.pattern_idx])
                if cmd == "rotate":
                    piece.pattern_idx = (piece.pattern_idx + 1) % len(piece.patterns)
                if cmd == "left":
                    if not any( elem in tetris.left_border for elem in piece.patterns[piece.pattern_idx]):
                        piece.patterns[piece.pattern_idx] -= 1
                if cmd == "right":
                    if not any( elem in tetris.right_border for elem in piece.patterns[piece.pattern_idx]):
                        piece.patterns[piece.pattern_idx] += 1
                piece.patterns[piece.pattern_idx] += tetris.C
                if tetris.check_2block(piece):
                    tetris.block_cells(pattern_copy)
                    piece = None
                    if any(elem in tetris.top_border for elem in pattern_copy):
                        tetris.print_board()
                        print("Game Over!")
                        break
            tetris.print_board(piece)
        else:  # dimensions command
            if re.match(r"\d+ \d+", cmd):
                cols, rows = map(int, cmd.split(" "))
                tetris = Tetris(rows, cols)
                tetris.print_board(piece)
            else:
                print("Error, unknown command")

if __name__ == "__main__":
    main()
