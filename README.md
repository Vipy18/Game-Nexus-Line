# Nexus Line

A modern, highly responsive 4-in-a-row game implemented in Python using Pygame. The game features a polished user interface, dynamic hover effects, and an intelligent AI decision engine.

Developed by **Vipul Deshmukh**

---

## 1. Game Overview & Features

Nexus Line is played on a **6x6 grid** where the goal is to align **4 consecutive markers** (horizontal, vertical, or diagonal) to win.

- **Board Size**: 6x6 Grid (`ROWS = 6`, `COLS = 6`).
- **Win Condition**: Connect 4 markers in a line (`WIN_LENGTH = 4`).
- **Markers**: `X` (Gold/Saffron) and `O` (Coral/Burnt Sienna).
- **Game Modes**:
  - **Player vs Player (PVP)**: Local hotseat multiplayer.
  - **Player vs AI (PVAI)**: Single-player mode against a highly strategic agent.
- **Premium UI / Visual Polish**:
  - Curated HSL-tailored color palette (Slate Gray, Persian Green, Saffron, Coral).
  - Modern typography using `Segoe UI` fonts.
  - Interactive menus with smooth hover effects.
  - Animated win-line highlight on victory.

---

## 2. Setup & Installation

### Prerequisites
- Python 3.10 or newer

### Quick Start

1. Clone or navigate to the project directory:
   ```bash
   cd d:/AIML/NexusLine
   ```

2. Activate the pre-configured virtual environment:
   - **Windows (PowerShell)**:
     ```powershell
     .venv\Scripts\Activate.ps1
     ```
   - **Windows (Command Prompt)**:
     ```cmd
     .venv\Scripts\activate.bat
     ```

3. Ensure Pygame is installed in your active virtual environment:
   ```bash
   pip install pygame
   ```

4. Run the game:
   ```bash
   python main.py
   ```

---

## 3. Architecture & Code Structure

The game structure is encapsulated inside `main.py` and is organized as follows:

```
├── .venv/                   # Virtual environment with Pygame installed
├── Game Report_ Nexus Line.pdf # Project design specification document
├── main.py                  # Core Python implementation
└── README.md                # Project documentation
```

### Core Classes & Methods

#### `Board` Class
Manages the grid state and transitions:
- `__init__()`: Initializes the 6x6 empty grid representation.
- `drop_piece(row, col, piece)`: Places a marker in an empty square.
- `is_valid_location(row, col)`: Checks if a cell is empty.
- `get_valid_locations()`: Returns a list of unoccupied (row, col) coordinates.
- `check_win(piece)`: Scans all horizontal, vertical, positive diagonal, and negative diagonal lines of length 4. Stores the winning coordinate path in `winning_line`.
- `is_draw()`: Returns `True` if no moves are left and no winner has been declared.
- `copy()`: Creates a deep copy of the board for search tree evaluation.

---

## 4. AI Decision Engine

The AI (`get_ai_move`) utilizes a layered strategy combining uninformed heuristics with depth-limited adversarial search.

```
                  [ get_ai_move() ]
                         │
        ┌────────────────┴────────────────┐
        ▼                                 ▼
[ Uninformed Search ]             [ Informed Search ]
(Immediate Wins/Blocks)          (Minimax + Alpha-Beta)
        │                                 │
        ▼ (If matched)                    ▼ (Fallback)
   Execute Move                      Depth-2 Search Tree
```

### A. Layer 1: Uninformed Search (Immediate Actions)
Before executing search algorithms, the AI runs quick checks:
1. **Immediate Win**: Scans all valid positions. If a move results in an immediate AI victory, it takes it.
2. **Immediate Block**: Scans all valid positions for the player. If the opponent has a move that results in an immediate victory, the AI places its piece there to block them.

### B. Layer 2: Informed Search (Strategic Planning)
If no immediate action is needed, the AI runs a depth-2 **Minimax Algorithm with Alpha-Beta Pruning** to select the most optimal long-term cell.

- **Minimax Tree**: Explores possible future board states, maximizing the AI's utility score while assuming the human player plays optimally to minimize it.
- **Alpha-Beta Pruning**: Prunes branches of the search tree that are guaranteed to yield worse results than previously examined states, significantly improving decision-making speed.

### C. Heuristic Scoring Parameters
Each simulated board state is evaluated by `score_position` using a rolling window of length 4. Points are awarded based on marker distribution:

| Configuration | Description | Score Value |
| :--- | :--- | :--- |
| **4 AI Markers** | Immediate win found | **+10,000** |
| **3 AI Markers + 1 Empty** | Open 3-in-a-row | **+50** |
| **2 AI Markers + 2 Empty** | Open 2-in-a-row | **+5** |
| **3 Player Markers + 1 Empty** | Opponent threatening win (High Block priority) | **-400** |
| **2 Player Markers + 2 Empty** | Opponent developing line | **-10** |

---

## 5. UI Layout Screens

The game flows through four beautifully styled screen sequences:
1. **Start Screen / Interactive Tutorial**: Displays game rules and connect-4 objectives.
2. **Main Menu**: Large button layouts to select between PVP and PVAI modes.
3. **Marker Selection**: Interactive character choice (`X` or `O`) before launching PVAI mode.
4. **Gameplay Interface**: A dark grid layout highlighting current turns, a thinking status bar, and an overlay screen to play again upon win or draw.
