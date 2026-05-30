# ai.py

import time

from board import (
    SIZE,
    WIN_LEN,
    EMPTY,
    HUMAN,
    AI,
    terminal_state
)



MOVE_RADIUS = 2
MAX_CANDIDATE_MOVES = 15


def is_inside_board(row, col):
    """
    Kiểm tra một ô có nằm trong bàn cờ hay không.

    Ví dụ:
    Bàn cờ 12x12 thì chỉ số hợp lệ là từ 0 đến 11.
    """
    if row < 0:
        return False

    if row >= SIZE:
        return False

    if col < 0:
        return False

    if col >= SIZE:
        return False

    return True


def get_occupied_cells(board):
    """
    Lấy danh sách các ô đã có quân X hoặc O trên bàn cờ.

    Tối ưu:
    - Thay vì mỗi lần generate_moves() và evaluate() đều tự quét toàn bộ bàn cờ,
      ta lấy danh sách này một lần ở gốc rồi cập nhật dần trong Minimax / Alpha-Beta.
    """
    occupied_cells = set()

    for row in range(SIZE):
        for col in range(SIZE):
            if board[row][col] != EMPTY:
                occupied_cells.add((row, col))

    return occupied_cells


def get_line_metrics(board, row, col, dr, dc, piece):
    total = 1
    open_ends = 0

    # Hướng tới
    r = row + dr
    c = col + dc
    while is_inside_board(r, c) and board[r][c] == piece:
        total += 1
        r += dr
        c += dc
    if is_inside_board(r, c) and board[r][c] == EMPTY:
        open_ends += 1

    # Hướng lui
    r = row - dr
    c = col - dc
    while is_inside_board(r, c) and board[r][c] == piece:
        total += 1
        r -= dr
        c -= dc
    if is_inside_board(r, c) and board[r][c] == EMPTY:
        open_ends += 1

    return total, open_ends

def local_pattern_score(board, row, col, piece):
    score = 0
    directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
    for dr, dc in directions:
        total, open_ends = get_line_metrics(board, row, col, dr, dc, piece)
        
        if total >= WIN_LEN:
            score += 100000000
        elif total == WIN_LEN - 1 and open_ends == 2:
            score += 10000000
        elif total == WIN_LEN - 1 and open_ends == 1:
            score += 1000000
        elif total == WIN_LEN - 2 and open_ends == 2:
            score += 100000
        elif total == WIN_LEN - 2 and open_ends == 1:
            score += 10000
        else:
            score += total * 10
            
    return score

def heuristic_move_score(board, move, current_player):
    """
    Chấm điểm nhanh (heuristic) một nước đi dựa trên các chuỗi cờ tạo thành.
    """
    row = move[0]
    col = move[1]
    
    opponent = HUMAN if current_player == AI else AI
    
    # Tính điểm Tấn công (nếu mình đánh vào ô này)
    attack_score = local_pattern_score(board, row, col, current_player)
    
    # Tính điểm Phòng thủ (nếu đối phương đánh vào ô này)
    block_score = local_pattern_score(board, row, col, opponent)
    
    # Nếu đánh vào thắng luôn, ưu tiên tuyệt đối
    if attack_score >= 100000000:
        return 200000000
        
    # Nếu đối phương đánh vào thắng luôn, bắt buộc phải chặn
    if block_score >= 100000000:
        return 150000000
        
    # Ưu tiên tấn công hơn một chút
    return attack_score * 2 + block_score


def generate_moves(board, current_player, radius=MOVE_RADIUS, max_candidate_moves=MAX_CANDIDATE_MOVES, occupied_cells=None):
    """
    Sinh danh sách nước đi ứng viên cho Minimax / Alpha-Beta.

    Chương trình không xét toàn bộ ô trống trên bàn cờ mà chỉ xét các ô trống
    nằm gần những quân đã đánh. Sau đó, các nước đi được sắp xếp theo điểm
    heuristic và chỉ giữ lại một số lượng ứng viên tốt nhất để giảm không gian tìm kiếm.
    """

    # Tối ưu:
    # Nếu đã có danh sách các ô đang có quân, dùng lại danh sách đó
    # thay vì quét toàn bộ bàn cờ ở mỗi node của Minimax / Alpha-Beta.
    if occupied_cells is None:
        occupied_cells = get_occupied_cells(board)

    moves = set()

    # Nếu bàn cờ chưa có quân nào, AI đánh vào giữa bàn
    if len(occupied_cells) == 0:
        center = SIZE // 2
        return [(center, center)]

    for row, col in occupied_cells:

        start_row = row - radius
        end_row = row + radius

        start_col = col - radius
        end_col = col + radius

        # Duyệt các ô xung quanh quân đã đánh
        for new_row in range(start_row, end_row + 1):
            for new_col in range(start_col, end_col + 1):

                # Nếu ô nằm ngoài bàn cờ thì bỏ qua
                if not is_inside_board(new_row, new_col):
                    continue

                # Nếu ô đang trống thì thêm vào danh sách nước đi
                if board[new_row][new_col] == EMPTY:
                    moves.add((new_row, new_col))

    # Chuyển set thành list để có thể sắp xếp
    move_list = list(moves)

    # Sắp xếp nước đi ưu tiên cao lên trước dựa vào độ nguy hiểm chiến thuật
    move_list.sort(key=lambda m: heuristic_move_score(board, m, current_player), reverse=True)

    # Giới hạn số nước đi ứng viên để giảm số nhánh trong cây tìm kiếm
    return move_list[:max_candidate_moves]


def score_sequence(length, open_ends, player):
    """
    Chấm điểm một chuỗi quân liên tiếp.

    length:
        Số quân liên tiếp.
        Ví dụ: OOO có length = 3.

    open_ends:
        Số đầu mở của chuỗi.
        0 = bị chặn cả hai đầu
        1 = mở một đầu
        2 = mở hai đầu

    player:
        AI hoặc HUMAN.

    Ví dụ:
        .OOO.  -> length = 3, open_ends = 2
        XOOO.  -> length = 3, open_ends = 1
        .O.    -> length = 1, open_ends = 2
        XO.    -> length = 1, open_ends = 1
    """

    score = 0

    # Có WIN_LEN quân liên tiếp hoặc hơn thì thắng
    if length >= WIN_LEN:
        score = 100000

    # 3 quân liên tiếp
    elif length == 3:

        # Ví dụ: .OOO.
        # Mở hai đầu, rất mạnh
        if open_ends == 2:
            score = 5000

        # Ví dụ: XOOO.
        # Bị chặn một đầu, vẫn mạnh nhưng yếu hơn .OOO.
        elif open_ends == 1:
            score = 1000

        # Ví dụ: XOOOX
        # Bị chặn hai đầu, gần như không còn giá trị
        else:
            score = 0

    # 2 quân liên tiếp
    elif length == 2:

        # Ví dụ: .OO.
        if open_ends == 2:
            score = 500

        # Ví dụ: XOO.
        elif open_ends == 1:
            score = 100

        # Ví dụ: XOOX
        else:
            score = 0

    # 1 quân đơn
    elif length == 1:

        # Ví dụ: .O.
        # Vẫn tốt hơn XO. nhưng điểm thấp
        if open_ends == 2:
            score = 20

        # Ví dụ: XO.
        elif open_ends == 1:
            score = 5

        # Ví dụ: XOX
        else:
            score = 0

    # Nếu là điểm của AI thì trả điểm dương
    if player == AI:
        return score

    # Nếu là điểm của người chơi thì trả điểm âm
    # Nhân mạnh hơn 20% để AI ưu tiên chặn người chơi
    if player == HUMAN:
        defensive_score = score + score // 5
        return -defensive_score

    return 0


def evaluate_direction(board, row, col, dr, dc, player):
    """
    Đánh giá một chuỗi quân liên tiếp bắt đầu từ ô (row, col)
    theo một hướng cụ thể.

    dr, dc là hướng đi.

    Ví dụ:
    dr = 0, dc = 1    -> ngang
    dr = 1, dc = 0    -> dọc
    dr = 1, dc = 1    -> chéo chính
    dr = 1, dc = -1   -> chéo phụ
    """

    length = 0

    current_row = row
    current_col = col

    # Đếm xem có bao nhiêu quân liên tiếp của player
    while True:

        if not is_inside_board(current_row, current_col):
            break

        if board[current_row][current_col] == player:
            length = length + 1
            current_row = current_row + dr
            current_col = current_col + dc
        else:
            break

    if length == 0:
        return 0

    open_ends = 0

    # Kiểm tra đầu trước của chuỗi
    before_row = row - dr
    before_col = col - dc

    if is_inside_board(before_row, before_col):
        if board[before_row][before_col] == EMPTY:
            open_ends = open_ends + 1

    # Kiểm tra đầu sau của chuỗi
    after_row = row + dr * length
    after_col = col + dc * length

    if is_inside_board(after_row, after_col):
        if board[after_row][after_col] == EMPTY:
            open_ends = open_ends + 1

    score = score_sequence(length, open_ends, player)

    return score


def evaluate(board, occupied_cells=None):
    """
    Đánh giá toàn bộ bàn cờ.

    Điểm dương:
        Bàn cờ đang có lợi cho AI.

    Điểm âm:
        Bàn cờ đang có lợi cho người chơi.

    Cách đánh giá:
    - Duyệt từng quân X và O trên bàn cờ.
    - Với mỗi quân, xét 4 hướng.
    - Đếm chuỗi quân liên tiếp.
    - Xem chuỗi đó mở hai đầu, một đầu hay bị chặn hai đầu.
    - Cộng điểm lại.
    """

    state = terminal_state(board)

    if state == "AI_WIN":
        return 1000000

    if state == "HUMAN_WIN":
        return -1000000

    if state == "DRAW":
        return 0

    total_score = 0

    directions = [
        (0, 1),    # ngang
        (1, 0),    # dọc
        (1, 1),    # chéo chính
        (1, -1)    # chéo phụ
    ]

    players = [AI, HUMAN]

    # Tối ưu hóa: Tìm Bounding Box chứa các quân cờ để giới hạn vòng lặp
    # Nếu Minimax / Alpha-Beta đã truyền occupied_cells vào,
    # dùng trực tiếp danh sách đó để tránh quét toàn bộ bàn cờ thêm lần nữa.
    if occupied_cells is None:
        occupied_cells = get_occupied_cells(board)

    # Nếu bàn cờ trống không có quân nào
    if len(occupied_cells) == 0:
        return 0

    min_row, max_row = SIZE, -1
    min_col, max_col = SIZE, -1

    for r, c in occupied_cells:
        if r < min_row: min_row = r
        if r > max_row: max_row = r
        if c < min_col: min_col = c
        if c > max_col: max_col = c

    for player in players:

        # Chỉ lặp qua phạm vi có quân cờ thay vì toàn bộ bàn cờ  (bounding box)
        for row in range(min_row, max_row + 1):
            for col in range(min_col, max_col + 1):

                # Chỉ bắt đầu đánh giá từ ô có quân của player
                if board[row][col] != player:
                    continue

                for direction in directions:

                    dr = direction[0]
                    dc = direction[1]

                    # Tránh tính trùng một chuỗi nhiều lần.
                    # Nếu ô phía trước cùng hướng đã là quân của player,
                    # nghĩa là ô hiện tại không phải điểm bắt đầu chuỗi.
                    previous_row = row - dr
                    previous_col = col - dc

                    if is_inside_board(previous_row, previous_col):
                        if board[previous_row][previous_col] == player:
                            continue

                    score = evaluate_direction(
                        board,
                        row,
                        col,
                        dr,
                        dc,
                        player
                    )

                    total_score = total_score + score

    return total_score



def terminal_score(state):
    """
    Trả điểm trực tiếp cho trạng thái kết thúc.

    Tối ưu:
    - minimax() và alphabeta() đã gọi terminal_state(board).
    - Không gọi evaluate(board) thêm một lần nữa để tránh kiểm tra trùng.
    """
    if state == "AI_WIN":
        return 1000000

    if state == "HUMAN_WIN":
        return -1000000

    if state == "DRAW":
        return 0

    return None


def minimax(board, depth, maximizing, stats, occupied_cells=None, radius=MOVE_RADIUS, max_candidate_moves=MAX_CANDIDATE_MOVES):
    """
    Thuật toán Minimax.

    AI là MAX:
        AI cố gắng chọn nước đi có điểm cao nhất.

    Người chơi là MIN:
        Người chơi được giả định sẽ chọn nước đi làm điểm AI thấp nhất.
    """

    stats["nodes"] = stats["nodes"] + 1

    state = terminal_state(board)

    # Nếu ván cờ đã kết thúc thì trả điểm
    if state is not None:
        score = terminal_score(state)
        return score, None

    if occupied_cells is None:
        occupied_cells = get_occupied_cells(board)

    # Nếu đã đạt giới hạn độ sâu thì dùng hàm đánh giá
    if depth == 0:
        score = evaluate(board, occupied_cells)
        return score, None

    current_player = AI if maximizing else HUMAN
    moves = generate_moves(board, current_player, radius=radius, max_candidate_moves=max_candidate_moves, occupied_cells=occupied_cells)

    if maximizing == True:

        best_score = float("-inf")
        best_move = None

        for move in moves:

            row = move[0]
            col = move[1]

            # Giả lập AI đánh vào ô này
            board[row][col] = AI
            occupied_cells.add(move)

            score, child_move = minimax(
                board,
                depth - 1,
                False,
                stats,
                occupied_cells,
                radius,
                max_candidate_moves
            )

            # Hoàn tác nước đi
            board[row][col] = EMPTY
            occupied_cells.remove(move)

            # Nếu điểm tốt hơn thì cập nhật
            if score > best_score:
                best_score = score
                best_move = move

        return best_score, best_move

    else:

        best_score = float("inf")
        best_move = None

        for move in moves:

            row = move[0]
            col = move[1]

            # Giả lập người chơi đánh vào ô này
            board[row][col] = HUMAN
            occupied_cells.add(move)

            score, child_move = minimax(
                board,
                depth - 1,
                True,
                stats,
                occupied_cells,
                radius,
                max_candidate_moves
            )

            # Hoàn tác nước đi
            board[row][col] = EMPTY
            occupied_cells.remove(move)

            # Người chơi chọn nước làm điểm AI thấp nhất
            if score < best_score:
                best_score = score
                best_move = move

        return best_score, best_move


def alphabeta(board, depth, alpha, beta, maximizing, stats, first_move=None, occupied_cells=None, radius=MOVE_RADIUS, max_candidate_moves=MAX_CANDIDATE_MOVES):
    """
    Thuật toán Alpha-Beta pruning có hỗ trợ Root Move Ordering.
    """

    stats["nodes"] = stats["nodes"] + 1

    state = terminal_state(board)

    # Nếu ván cờ đã kết thúc thì trả điểm
    if state is not None:
        score = terminal_score(state)
        return score, None

    if occupied_cells is None:
        occupied_cells = get_occupied_cells(board)

    # Nếu đã đạt giới hạn độ sâu thì dùng hàm đánh giá
    if depth == 0:
        score = evaluate(board, occupied_cells)
        return score, None

    current_player = AI if maximizing else HUMAN
    moves = generate_moves(board, current_player, radius=radius, max_candidate_moves=max_candidate_moves, occupied_cells=occupied_cells)
    
    # Root Move Ordering: Mang nước đi tốt nhất từ vòng lặp trước lên đầu danh sách để thử nghiệm đầu tiên
    if first_move is not None and first_move in moves:
        moves.remove(first_move)
        moves.insert(0, first_move)

    if maximizing == True:

        best_score = float("-inf")
        best_move = None

        for move in moves:

            row = move[0]
            col = move[1]

            # Giả lập AI đánh
            board[row][col] = AI
            occupied_cells.add(move)

            score, child_move = alphabeta(
                board,
                depth - 1,
                alpha,
                beta,
                False,
                stats,
                occupied_cells=occupied_cells,
                radius=radius,
                max_candidate_moves=max_candidate_moves
            )

            # Hoàn tác nước đi
            board[row][col] = EMPTY
            occupied_cells.remove(move)

            if score > best_score:
                best_score = score
                best_move = move

            if best_score > alpha:
                alpha = best_score

            # Cắt nhánh
            if beta <= alpha:
                stats["cutoffs"] = stats["cutoffs"] + 1
                break

        return best_score, best_move

    else:

        best_score = float("inf")
        best_move = None

        for move in moves:

            row = move[0]
            col = move[1]

            # Giả lập người chơi đánh
            board[row][col] = HUMAN
            occupied_cells.add(move)

            score, child_move = alphabeta(
                board,
                depth - 1,
                alpha,
                beta,
                True,
                stats,
                occupied_cells=occupied_cells,
                radius=radius,
                max_candidate_moves=max_candidate_moves
            )

            # Hoàn tác nước đi
            board[row][col] = EMPTY
            occupied_cells.remove(move)

            if score < best_score:
                best_score = score
                best_move = move

            if best_score < beta:
                beta = best_score

            # Cắt nhánh
            if beta <= alpha:
                stats["cutoffs"] = stats["cutoffs"] + 1
                break

        return best_score, best_move


def choose_ai_move(board, depth=2, algorithm="alphabeta", radius=MOVE_RADIUS, max_candidate_moves=MAX_CANDIDATE_MOVES):
    """
    Hàm chọn nước đi cho AI. Tích hợp Iterative Deepening.
    """

    start_time = time.perf_counter()

    stats = {
        "nodes": 0,
        "cutoffs": 0
    }

    best_move_overall = None
    best_score_overall = 0
    occupied_cells = get_occupied_cells(board)

    # TỐI ƯU KHAI CUỘC: Khi bàn cờ gần trống (≤ 2 quân),
    # alpha-beta gần như không cắt được nhánh nào vì mọi đánh giá đều ~0.
    # Giảm depth xuống tối đa 3 vì nước khai cuộc chất lượng gần như nhau.
    if len(occupied_cells) <= 2:
        depth = min(depth, 3)

    if algorithm == "minimax":

        score, move = minimax(
            board,
            depth,
            True,
            stats,
            occupied_cells,
            radius,
            max_candidate_moves
        )
        best_move_overall = move
        best_score_overall = score

    elif algorithm == "alphabeta":

        # Khám phá dần dần (Iterative Deepening)
        for current_depth in range(1, depth + 1):
            score, move = alphabeta(
                board,
                current_depth,
                float("-inf"),
                float("inf"),
                True,
                stats,
                first_move=best_move_overall,
                occupied_cells=occupied_cells,
                radius=radius,
                max_candidate_moves=max_candidate_moves
            )
            
            if move is not None:
                best_move_overall = move
                best_score_overall = score
                
            # Nếu phát hiện một nhánh dẫn đến chiến thắng tuyệt đối, ngắt sớm
            if score >= 900000:
                break

    else:
        raise ValueError("Algorithm must be 'minimax' or 'alphabeta'.")

    end_time = time.perf_counter()

    running_time = end_time - start_time

    result = {
        "move": best_move_overall,
        "score": best_score_overall,
        "nodes": stats["nodes"],
        "cutoffs": stats["cutoffs"],
        "time": running_time,
        "depth": depth,
        "algorithm": algorithm
    }

    return result