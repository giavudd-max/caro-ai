# main.py

from board import (
    create_board,
    print_board,
    is_valid_move,
    terminal_state,
    HUMAN,
    AI
)

from ai import choose_ai_move


def ask_human_move(board):
    """
    Hàm nhập nước đi của người chơi.

    Người chơi nhập theo dạng:
    row col

    Ví dụ:
    5 6
    nghĩa là đánh vào hàng 5, cột 6.
    """

    while True:
        user_input = input("Enter your move row col, example 5 6: ")

        parts = user_input.split()

        if len(parts) != 2:
            print("Invalid input. Please enter two numbers, example: 5 6")
            continue

        try:
            row = int(parts[0])
            col = int(parts[1])
        except ValueError:
            print("Invalid input. Row and column must be numbers.")
            continue

        if is_valid_move(board, row, col):
            return row, col
        else:
            print("Invalid move. The cell is outside the board or already occupied.")


def print_game_result(board):
    """
    Hàm in kết quả cuối cùng của ván cờ.
    """

    state = terminal_state(board)

    if state == "AI_WIN":
        print("AI wins.")

    elif state == "HUMAN_WIN":
        print("Human wins.")

    elif state == "DRAW":
        print("Draw.")

    else:
        print("Game is not finished.")


def choose_algorithm():
    """
    Cho người dùng chọn thuật toán AI.
    """

    print("Choose AI algorithm:")
    print("1. Minimax")
    print("2. Alpha-Beta")

    choice = input("Enter your choice, 1 or 2: ")

    if choice == "1":
        return "minimax"

    if choice == "2":
        return "alphabeta"

    print("Invalid choice. Default algorithm is Alpha-Beta.")
    return "alphabeta"


def choose_depth():
    """
    Cho người dùng chọn độ sâu tìm kiếm.
    """

    user_input = input("Enter search depth, recommended 1 or 2: ")

    try:
        depth = int(user_input)
    except ValueError:
        print("Invalid depth. Default depth is 2.")
        return 2

    if depth < 1:
        print("Depth must be at least 1. Default depth is 2.")
        return 2

    return depth


def play_game():
    """
    Hàm chính để chạy game Caro người chơi đấu với AI.
    """

    board = create_board()

    print("===================================")
    print("        CARO AI GAME")
    print("===================================")
    print("Human player: X")
    print("AI player: O")
    print("Win condition: 4 consecutive pieces")
    print("Input format: row col")
    print("Example: 5 6")
    print("===================================")

    algorithm = choose_algorithm()
    depth = choose_depth()

    while True:
        print_board(board)

        # Lượt người chơi
        print("Your turn.")
        human_row, human_col = ask_human_move(board)
        board[human_row][human_col] = HUMAN

        # Kiểm tra sau lượt người chơi
        if terminal_state(board) is not None:
            break

        # Lượt AI
        print()
        print("AI is thinking...")

        result = choose_ai_move(
            board,
            depth=depth,
            algorithm=algorithm
        )

        ai_move = result["move"]

        if ai_move is None:
            break

        ai_row = ai_move[0]
        ai_col = ai_move[1]

        board[ai_row][ai_col] = AI

        print()
        print("AI move:", ai_move)
        print("Algorithm:", result["algorithm"])
        print("Depth:", result["depth"])
        print("Score:", result["score"])
        print("Nodes searched:", result["nodes"])
        print("Cutoffs:", result["cutoffs"])
        print("Time:", round(result["time"], 6), "seconds")

        # Kiểm tra sau lượt AI
        if terminal_state(board) is not None:
            break

    print_board(board)
    print_game_result(board)


if __name__ == "__main__":
    play_game()