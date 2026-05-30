# Caro AI

## 1. Description

This project implements a Caro game between a human player and an AI player.

- Board size: 12x12
- Human player: X
- AI player: O
- Empty cell: .
- Win condition: 4 consecutive pieces horizontally, vertically, or diagonally
- The program does not require open-ended lines for winning
- Algorithms:
  - Minimax
  - Alpha-Beta pruning

## 2. Features

- Console version for basic gameplay
- Graphical interface using Tkinter
- Human vs AI gameplay
- Choose who moves first: Human or AI
- Choose AI algorithm: Minimax or Alpha-Beta
- Difficulty modes:
  - Easy: depth 3
  - Medium: depth 6
  - Hard: depth 9
- Undo one turn
- Restart / New game
- Show AI move, algorithm, depth, score, searched nodes, cutoffs, and running time
- Benchmark Minimax and Alpha-Beta on multiple board states

## 3. Requirements

The project uses Python standard libraries only.

Tkinter is required for the GUI and is usually included with standard Python installations.

No external packages are required.

## 4. Project Structure

```text
caro-ai/
├── README.md
├── requirements.txt
├── .gitignore
└── source_code/
    ├── ai.py
    ├── benchmark.py
    ├── benchmark_results.csv
    ├── board.py
    ├── gui.py
    └── main.py
```

## 5. Run GUI Version

```bash
cd source_code
python gui.py
```

## 6. Run Console Version

```bash
cd source_code
python main.py
```

## 7. Run Benchmark

```bash
cd source_code
python benchmark.py
```

The benchmark compares Minimax and Alpha-Beta on the same board states, using the same depth, evaluation function, radius, and maximum number of candidate moves.

The output includes:

- selected move
- evaluation score
- number of searched nodes
- number of Alpha-Beta cutoffs
- running time

Benchmark results are saved to:

```text
benchmark_results.csv
```

## 8. Notes

Depth 4 may take longer for Minimax because Minimax expands many more states than Alpha-Beta.

For a quick test, use smaller depths such as 1 or 2.

For reproducing the report results, use the configured benchmark depths in `benchmark.py`.
