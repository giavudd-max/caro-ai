import copy
import threading
import tkinter as tk
from tkinter import messagebox

from board import (
    SIZE,
    EMPTY,
    HUMAN,
    AI,
    create_board,
    is_valid_move,
    terminal_state
)

from ai import choose_ai_move


DIFFICULTY_CONFIG = {
    "easy": {
        "label": "Easy - depth 3",
        "depth": 3,
        "radius": 2,
        "max_candidate_moves": 20
    },
    "medium": {
        "label": "Medium - depth 6",
        "depth": 6,
        "radius": 2,
        "max_candidate_moves": 15
    },
    "hard": {
        "label": "Hard - depth 9",
        "depth": 9,
        "radius": 2,
        "max_candidate_moves": 10
    }
}


class CaroGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Caro AI - Optimized Version")

        self.board = create_board()
        self.buttons = []
        self.move_history = []
        self.game_over = False
        self.ai_thinking = False
        self.game_id = 0

        self.first_player_var = tk.StringVar(value="human")
        self.difficulty_var = tk.StringVar(value="medium")
        self.algorithm_var = tk.StringVar(value="alphabeta")

        self.current_turn = HUMAN

        self.build_layout()
        self.update_status("Choose settings, then click New Game.")
        self.set_board_enabled(False)

    # ======================================================
    # UI LAYOUT
    # ======================================================

    def build_layout(self):
        main_frame = tk.Frame(self.root, padx=10, pady=10)
        main_frame.pack()

        self.board_frame = tk.Frame(main_frame)
        self.board_frame.grid(row=0, column=0)

        control_frame = tk.Frame(main_frame, padx=15)
        control_frame.grid(row=0, column=1, sticky="n")

        self.create_board_buttons()
        self.create_controls(control_frame)

    def create_board_buttons(self):
        for row in range(SIZE):
            button_row = []

            for col in range(SIZE):
                button = tk.Button(
                    self.board_frame,
                    text="",
                    width=3,
                    height=1,
                    font=("Arial", 14, "bold"),
                    command=lambda r=row, c=col: self.handle_cell_click(r, c)
                )

                button.grid(row=row, column=col, padx=1, pady=1)
                button_row.append(button)

            self.buttons.append(button_row)

    def create_controls(self, parent):
        title = tk.Label(
            parent,
            text="CARO AI",
            font=("Arial", 18, "bold")
        )
        title.pack(pady=(0, 10))

        first_player_label = tk.Label(parent, text="First move:", font=("Arial", 11, "bold"))
        first_player_label.pack(anchor="w")

        tk.Radiobutton(
            parent,
            text="Human first (X)",
            variable=self.first_player_var,
            value="human"
        ).pack(anchor="w")

        tk.Radiobutton(
            parent,
            text="AI first (O)",
            variable=self.first_player_var,
            value="ai"
        ).pack(anchor="w")

        difficulty_label = tk.Label(parent, text="Difficulty:", font=("Arial", 11, "bold"))
        difficulty_label.pack(anchor="w", pady=(12, 0))

        for key in DIFFICULTY_CONFIG:
            tk.Radiobutton(
                parent,
                text=DIFFICULTY_CONFIG[key]["label"],
                variable=self.difficulty_var,
                value=key
            ).pack(anchor="w")

        algorithm_label = tk.Label(parent, text="Algorithm:", font=("Arial", 11, "bold"))
        algorithm_label.pack(anchor="w", pady=(12, 0))

        tk.Radiobutton(
            parent,
            text="Alpha-Beta",
            variable=self.algorithm_var,
            value="alphabeta"
        ).pack(anchor="w")

        tk.Radiobutton(
            parent,
            text="Minimax",
            variable=self.algorithm_var,
            value="minimax"
        ).pack(anchor="w")

        self.new_game_button = tk.Button(
            parent,
            text="New Game / Restart",
            width=22,
            command=self.start_new_game
        )
        self.new_game_button.pack(pady=(15, 5))

        self.undo_button = tk.Button(
            parent,
            text="Undo 1 Turn",
            width=22,
            command=self.undo_one_turn
        )
        self.undo_button.pack(pady=5)

        self.status_label = tk.Label(
            parent,
            text="",
            width=35,
            justify="left",
            anchor="w",
            wraplength=250,
            font=("Arial", 10)
        )
        self.status_label.pack(pady=(15, 5), anchor="w")

        self.info_label = tk.Label(
            parent,
            text="",
            width=35,
            justify="left",
            anchor="w",
            wraplength=250,
            font=("Arial", 10)
        )
        self.info_label.pack(pady=5, anchor="w")

    # ======================================================
    # GAME CONTROL
    # ======================================================

    def start_new_game(self):
        self.game_id = self.game_id + 1
        self.board = create_board()
        self.move_history = []
        self.game_over = False
        self.ai_thinking = False
        self.clear_board_ui()
        self.set_board_enabled(True)
        self.clear_info()

        if self.first_player_var.get() == "ai":
            self.current_turn = AI
            self.update_status("New game. AI moves first.")
            self.root.after(200, self.make_ai_move)
        else:
            self.current_turn = HUMAN
            self.update_status("New game. Your turn.")

    def clear_board_ui(self):
        for row in range(SIZE):
            for col in range(SIZE):
                self.buttons[row][col].config(text="", state="normal")

    def set_board_enabled(self, enabled):
        for row in range(SIZE):
            for col in range(SIZE):
                if self.board[row][col] != EMPTY:
                    self.buttons[row][col].config(state="disabled")
                else:
                    if enabled:
                        self.buttons[row][col].config(state="normal")
                    else:
                        self.buttons[row][col].config(state="disabled")

    def handle_cell_click(self, row, col):
        if self.game_over:
            return

        if self.ai_thinking:
            return

        if self.current_turn != HUMAN:
            return

        if not is_valid_move(self.board, row, col):
            return

        self.place_move(row, col, HUMAN)

        if self.check_and_finish_game():
            return

        self.current_turn = AI
        self.make_ai_move()

    def place_move(self, row, col, player):
        self.board[row][col] = player
        self.move_history.append((row, col, player))

        self.buttons[row][col].config(text=player, state="disabled")

        if player == HUMAN:
            self.buttons[row][col].config(fg="blue")
        else:
            self.buttons[row][col].config(fg="red")

    def check_and_finish_game(self):
        state = terminal_state(self.board)

        if state is None:
            return False

        self.game_over = True
        self.set_board_enabled(False)

        if state == "AI_WIN":
            self.update_status("Game over. AI wins.")
            messagebox.showinfo("Game Over", "AI wins.")

        elif state == "HUMAN_WIN":
            self.update_status("Game over. Human wins.")
            messagebox.showinfo("Game Over", "Human wins.")

        elif state == "DRAW":
            self.update_status("Game over. Draw.")
            messagebox.showinfo("Game Over", "Draw.")

        return True

    # ======================================================
    # AI MOVE
    # ======================================================

    def make_ai_move(self):
        if self.game_over:
            return

        if self.ai_thinking:
            return

        self.ai_thinking = True
        self.set_board_enabled(False)
        self.update_status("AI is thinking...")

        current_game_id = self.game_id
        board_copy = copy.deepcopy(self.board)

        difficulty_key = self.difficulty_var.get()
        config = DIFFICULTY_CONFIG[difficulty_key]

        depth = config["depth"]
        radius = config["radius"]
        max_candidate_moves = config["max_candidate_moves"]
        algorithm = self.algorithm_var.get()

        thread = threading.Thread(
            target=self.run_ai_search,
            args=(
                current_game_id,
                board_copy,
                depth,
                radius,
                max_candidate_moves,
                algorithm
            ),
            daemon=True
        )

        thread.start()

    def run_ai_search(self, game_id, board_copy, depth, radius, max_candidate_moves, algorithm):
        try:
            result = choose_ai_move(
                board_copy,
                depth=depth,
                algorithm=algorithm,
                radius=radius,
                max_candidate_moves=max_candidate_moves
            )

            self.root.after(0, lambda: self.apply_ai_result(game_id, result))

        except Exception as error:
            self.root.after(0, lambda error=error: self.handle_ai_error(error))

    def apply_ai_result(self, game_id, result):
        if game_id != self.game_id:
            return

        self.ai_thinking = False

        if self.game_over:
            return

        ai_move = result["move"]

        if ai_move is None:
            self.update_status("AI has no valid move.")
            self.set_board_enabled(False)
            return

        row = ai_move[0]
        col = ai_move[1]

        if is_valid_move(self.board, row, col):
            self.place_move(row, col, AI)

        self.update_info(result)

        if self.check_and_finish_game():
            return

        self.current_turn = HUMAN
        self.set_board_enabled(True)
        self.update_status("Your turn.")

    def handle_ai_error(self, error):
        self.ai_thinking = False
        self.set_board_enabled(True)
        self.update_status("AI error. Check terminal for details.")
        print("AI error:", error)

    # ======================================================
    # UNDO
    # ======================================================

    def undo_one_turn(self):
        """
        Hoàn tác một lượt gần nhất.
        Nếu lượt gần nhất gồm Human + AI, hàm sẽ xóa cả 2 nước.
        Cách này giúp người chơi quay lại trạng thái trước lượt vừa rồi.
        """
        if self.ai_thinking:
            messagebox.showwarning("Undo", "Cannot undo while AI is thinking.")
            return

        if len(self.move_history) == 0:
            return

        self.game_over = False

        # Nếu nước cuối là AI, xóa nước AI trước
        if len(self.move_history) > 0 and self.move_history[-1][2] == AI:
            self.remove_last_move()

        # Sau đó xóa nước HUMAN gần nhất nếu có
        if len(self.move_history) > 0 and self.move_history[-1][2] == HUMAN:
            self.remove_last_move()

        self.current_turn = HUMAN
        self.set_board_enabled(True)
        self.update_status("Undo completed. Your turn.")
        self.clear_info()

    def remove_last_move(self):
        row, col, player = self.move_history.pop()
        self.board[row][col] = EMPTY
        self.buttons[row][col].config(text="", state="normal")

    # ======================================================
    # TEXT STATUS
    # ======================================================

    def update_status(self, message):
        self.status_label.config(text="Status: " + message)

    def update_info(self, result):
        reason_str = result.get("reason", "Search")
        text = (
            "Last AI result:\n"
            + "Move: " + str(result["move"]) + "\n"
            + "Reason: " + str(reason_str) + "\n"
            + "Algorithm: " + str(result["algorithm"]) + "\n"
            + "Depth: " + str(result["depth"]) + "\n"
            + "Score: " + str(result["score"]) + "\n"
            + "Nodes: " + str(result["nodes"]) + "\n"
            + "Cutoffs: " + str(result["cutoffs"]) + "\n"
            + "Time: " + str(round(result["time"], 6)) + "s"
        )

        self.info_label.config(text=text)

    def clear_info(self):
        self.info_label.config(text="")


if __name__ == "__main__":
    root = tk.Tk()
    app = CaroGUI(root)
    root.mainloop()
