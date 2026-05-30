# board.py

SIZE = 12
WIN_LEN = 4

EMPTY = "."
HUMAN = "X"
AI = "O"


def create_board():
    board = []

    for row_index in range(SIZE):
        row = []

        for col_index in range(SIZE):
            row.append(EMPTY)

        board.append(row)

    return board


def print_board(board):
    print()

    print("   ", end="")

    for col_index in range(SIZE):
        print(f"{col_index:2}", end=" ")

    print()

    for row_index in range(SIZE):
        print(f"{row_index:2}", end="  ")

        for col_index in range(SIZE):
            print(f"{board[row_index][col_index]:2}", end=" ")

        print()

    print()


def is_valid_move(board, row, col):
    if row < 0:
        return False

    if row >= SIZE:
        return False

    if col < 0:
        return False

    if col >= SIZE:
        return False

    if board[row][col] != EMPTY:
        return False

    return True


def is_full(board):
    for row_index in range(SIZE):
        for col_index in range(SIZE):
            if board[row_index][col_index] == EMPTY:
                return False

    return True


def check_win(board, player):
    directions = [
        (0, 1),
        (1, 0),
        (1, 1),
        (1, -1)
    ]

    for row in range(SIZE):
        for col in range(SIZE):

            if board[row][col] != player:
                continue

            for direction in directions:
                dr = direction[0]
                dc = direction[1]

                count = 0

                for k in range(WIN_LEN):
                    new_row = row + dr * k
                    new_col = col + dc * k

                    if new_row < 0:
                        break

                    if new_row >= SIZE:
                        break

                    if new_col < 0:
                        break

                    if new_col >= SIZE:
                        break

                    if board[new_row][new_col] == player:
                        count = count + 1
                    else:
                        break

                if count == WIN_LEN:
                    return True

    return False


def terminal_state(board):
    if check_win(board, AI):
        return "AI_WIN"

    if check_win(board, HUMAN):
        return "HUMAN_WIN"

    if is_full(board):
        return "DRAW"

    return None

if __name__ == "__main__":
    board = create_board()
    print_board(board)