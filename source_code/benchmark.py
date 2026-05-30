import csv
import time

from ai import (
    minimax,
    alphabeta,
    get_occupied_cells,
    MOVE_RADIUS,
    MAX_CANDIDATE_MOVES
)


def board_from_strings(rows):
    """
    Chuyển board từ list chuỗi sang list 2 chiều.
    Mỗi chuỗi phải có đúng 12 ký tự.
    """
    board = []

    for row in rows:
        board.append(list(row))

    return board


def create_test_boards():
    """
    Tạo ít nhất 5 trạng thái kiểm thử theo yêu cầu đề.
    """
    test_boards = []

    # Test 1: Đầu ván
    test_boards.append({
        "name": "Early game",
        "board": board_from_strings([
            "............",
            "............",
            "............",
            "............",
            "............",
            ".....X......",
            "............",
            "............",
            "............",
            "............",
            "............",
            "............",
        ])
    })

    # Test 2: Giữa ván
    test_boards.append({
        "name": "Middle game",
        "board": board_from_strings([
            "............",
            "............",
            "...X........",
            "..OX........",
            "..XOO.......",
            "....X.O.....",
            "......X.....",
            "............",
            "............",
            "............",
            "............",
            "............",
        ])
    })

    # Test 3: AI có thể thắng ngay
    test_boards.append({
        "name": "AI immediate win",
        "board": board_from_strings([
            "............",
            "............",
            "..X.........",
            ".XOOO.......",
            "..XX........",
            "............",
            "............",
            "............",
            "............",
            "............",
            "............",
            "............",
        ])
    })

    # Test 4: Human sắp thắng, AI cần chặn
    test_boards.append({
        "name": "Human immediate threat",
        "board": board_from_strings([
            "............",
            "............",
            "............",
            "..OXXX......",
            "..OX........",
            ".....O......",
            "............",
            "............",
            "............",
            "............",
            "............",
            "............",
        ])
    })

    # Test 5: Hai bên đều có cơ hội
    test_boards.append({
        "name": "Both sides attacking",
        "board": board_from_strings([
            "............",
            "............",
            "..OX........",
            "...X.O......",
            "...OXO......",
            ".....XOX....",
            "....X.OX....",
            "............",
            "............",
            "............",
            "............",
            "............",
        ])
    })

    # Test 6: Nhiều quân, nhiều nhánh
    test_boards.append({
        "name": "Dense branching state",
        "board": board_from_strings([
            "............",
            ".....X......",
            "..X.O.......",
            "..OX.X......",
            "...XO.O.....",
            "..O.XO......",
            "....X.......",
            "....X.......",
            "....O.......",
            "............",
            "............",
            "............",
        ])
    })

    return test_boards


def run_single_case(
    test_index,
    test_name,
    board,
    depth,
    algorithm,
    radius=MOVE_RADIUS,
    max_candidate_moves=MAX_CANDIDATE_MOVES
):
    board_copy = []

    for row in board:
        board_copy.append(row[:])

    stats = {
        "nodes": 0,
        "cutoffs": 0
    }

    occupied_cells = get_occupied_cells(board_copy)

    start_time = time.perf_counter()

    if algorithm == "minimax":
        score, move = minimax(
            board_copy,
            depth,
            True,
            stats,
            occupied_cells,
            radius,
            max_candidate_moves
        )

    elif algorithm == "alphabeta":
        score, move = alphabeta(
            board_copy,
            depth,
            float("-inf"),
            float("inf"),
            True,
            stats,
            first_move=None,
            occupied_cells=occupied_cells,
            radius=radius,
            max_candidate_moves=max_candidate_moves
        )

    else:
        raise ValueError("Algorithm must be 'minimax' or 'alphabeta'.")

    end_time = time.perf_counter()
    running_time = end_time - start_time

    output = {
        "test_case": test_index,
        "test_name": test_name,
        "depth": depth,
        "algorithm": algorithm,
        "radius": radius,
        "max_candidate_moves": max_candidate_moves,
        "move": move,
        "score": score,
        "nodes": stats["nodes"],
        "cutoffs": stats["cutoffs"],
        "time": running_time
    }

    return output


def run_benchmark():
    test_boards = create_test_boards()

    # Depth 1, 2, 4 dùng để so sánh công bằng giữa Minimax và Alpha-Beta.
    # Depth 4 giúp thể hiện rõ hơn sự khác biệt về số node và thời gian chạy.

    depths = [1, 2, 4]
    algorithms = ["minimax", "alphabeta"]

    # Cấu hình sinh nước đi dùng chung cho cả Minimax và Alpha-Beta.
    # Hai thuật toán phải dùng cùng radius và max_candidate_moves để so sánh công bằng.
    radius = MOVE_RADIUS
    max_candidate_moves = MAX_CANDIDATE_MOVES

    results = []

    print("Benchmark: Minimax vs Alpha-Beta")
    print("=" * 145)

    header = (
        f"{'Test':<6}"
        f"{'Name':<25}"
        f"{'Depth':<8}"
        f"{'Algorithm':<12}"
        f"{'Radius':<8}"
        f"{'MaxMoves':<10}"
        f"{'Move':<12}"
        f"{'Score':<12}"
        f"{'Nodes':<12}"
        f"{'Cutoffs':<10}"
        f"{'Time(s)':<12}"
    )

    print(header)
    print("-" * 145)

    for index, test in enumerate(test_boards, start=1):
        for depth in depths:
            for algorithm in algorithms:
                result = run_single_case(
                    index,
                    test["name"],
                    test["board"],
                    depth,
                    algorithm,
                    radius,
                    max_candidate_moves
                )

                results.append(result)

                print(
                    f"{result['test_case']:<6}"
                    f"{result['test_name']:<25}"
                    f"{result['depth']:<8}"
                    f"{result['algorithm']:<12}"
                    f"{result['radius']:<8}"
                    f"{result['max_candidate_moves']:<10}"
                    f"{str(result['move']):<12}"
                    f"{result['score']:<12}"
                    f"{result['nodes']:<12}"
                    f"{result['cutoffs']:<10}"
                    f"{result['time']:<12.6f}"
                )

        print("-" * 145)

    save_results_to_csv(results)
    print("Saved benchmark results to benchmark_results.csv")


def save_results_to_csv(results):
    filename = "benchmark_results.csv"

    fieldnames = [
        "test_case",
        "test_name",
        "depth",
        "algorithm",
        "radius",
        "max_candidate_moves",
        "move",
        "score",
        "nodes",
        "cutoffs",
        "time"
    ]

    with open(filename, "w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()

        for result in results:
            writer.writerow(result)


if __name__ == "__main__":
    run_benchmark()
