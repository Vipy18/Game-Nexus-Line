import pygame
import sys
import math
import random
import time

# --- Constants ---
# Game Rules
ROWS = 6
COLS = 6
WIN_LENGTH = 4 # 4-in-a-row to win on a 6x6 grid

# UI & Theming
SQUARESIZE = 110
WIDTH = COLS * SQUARESIZE
HEIGHT = (ROWS + 1) * SQUARESIZE
size = (WIDTH, HEIGHT)
RADIUS = int(SQUARESIZE / 2 - 15)

# Color Palette
BACKGROUND_COLOR = (38, 70, 83) # Dark Slate Gray
GRID_COLOR = (42, 157, 143) # Persian Green
PLAYER_X_COLOR = (233, 196, 106) # Saffron/Gold
PLAYER_O_COLOR = (231, 111, 81) # Burnt Sienna/Coral
BUTTON_COLOR = (42, 157, 143)
BUTTON_HOVER_COLOR = (62, 177, 163) # Lighter green for hover
TEXT_COLOR = (255, 255, 255)
WIN_COLOR = (255, 255, 255) # White for high contrast win line
HIGHLIGHT_TEXT_COLOR = (244, 162, 97) # Sandy Brown for highlights

# --- Game Setup ---
pygame.init()
screen = pygame.display.set_mode(size)
pygame.display.set_caption("Nexus Line")
myfont = pygame.font.SysFont("Segoe UI", 50, bold=True)
smallfont = pygame.font.SysFont("Segoe UI", 30)
tutorialfont = pygame.font.SysFont("Segoe UI", 28)

# --- Game Logic and Board Class ---
class Board:
    def __init__(self):
        """Initializes the 6x6 board."""
        self.board = [['' for _ in range(COLS)] for _ in range(ROWS)]
        self.winner = None
        self.winning_line = []

    def drop_piece(self, row, col, piece):
        """Places a piece on the board."""
        if self.board[row][col] == '':
            self.board[row][col] = piece
            return True
        return False

    def is_valid_location(self, row, col):
        """Checks if a location is empty."""
        return self.board[row][col] == ''

    def get_valid_locations(self):
        """Returns a list of all empty (row, col) tuples."""
        return [(r, c) for r in range(ROWS) for c in range(COLS) if self.is_valid_location(r, c)]

    def check_win(self, piece):
        """Checks for a winning condition for the given piece."""
        # Check horizontal
        for r in range(ROWS):
            for c in range(COLS - (WIN_LENGTH - 1)):
                if all(self.board[r][c+i] == piece for i in range(WIN_LENGTH)):
                    self.winner = piece
                    self.winning_line = [(r, c+i) for i in range(WIN_LENGTH)]
                    return True
        # Check vertical
        for c in range(COLS):
            for r in range(ROWS - (WIN_LENGTH - 1)):
                if all(self.board[r+i][c] == piece for i in range(WIN_LENGTH)):
                    self.winner = piece
                    self.winning_line = [(r+i, c) for i in range(WIN_LENGTH)]
                    return True
        # Check positive diagonal
        for r in range(ROWS - (WIN_LENGTH - 1)):
            for c in range(COLS - (WIN_LENGTH - 1)):
                if all(self.board[r+i][c+i] == piece for i in range(WIN_LENGTH)):
                    self.winner = piece
                    self.winning_line = [(r+i, c+i) for i in range(WIN_LENGTH)]
                    return True
        # Check negative diagonal
        for r in range(WIN_LENGTH - 1, ROWS):
            for c in range(COLS - (WIN_LENGTH - 1)):
                if all(self.board[r-i][c+i] == piece for i in range(WIN_LENGTH)):
                    self.winner = piece
                    self.winning_line = [(r-i, c+i) for i in range(WIN_LENGTH)]
                    return True
        return False

    def is_draw(self):
        """Checks if the board is full."""
        return len(self.get_valid_locations()) == 0

    def copy(self):
        """Creates a deep copy of the board."""
        new_board = Board()
        new_board.board = [row[:] for row in self.board]
        return new_board

# --- AI Algorithms ---
def evaluate_window(window, ai_piece, player_piece):
    """Heuristic function to score a single window of WIN_LENGTH spaces."""
    score = 0
    if window.count(ai_piece) == 4:
        score += 10000
    elif window.count(ai_piece) == 3 and window.count('') == 1:
        score += 50
    elif window.count(ai_piece) == 2 and window.count('') == 2:
        score += 5
    if window.count(player_piece) == 3 and window.count('') == 1:
        score -= 400  # High penalty to encourage blocking
    elif window.count(player_piece) == 2 and window.count('') == 2:
        score -= 10
    return score

def score_position(board, ai_piece, player_piece):
    """Scores the entire board based on the piece's position."""
    score = 0
    # Horizontal
    for r in range(ROWS):
        for c in range(COLS - WIN_LENGTH + 1):
            window = board.board[r][c:c+WIN_LENGTH]
            score += evaluate_window(window, ai_piece, player_piece)
    # Vertical
    for c in range(COLS):
        for r in range(ROWS - WIN_LENGTH + 1):
            window = [board.board[r+i][c] for i in range(WIN_LENGTH)]
            score += evaluate_window(window, ai_piece, player_piece)
    # Diagonals
    for r in range(ROWS - WIN_LENGTH + 1):
        for c in range(COLS - WIN_LENGTH + 1):
            window = [board.board[r+i][c+i] for i in range(WIN_LENGTH)]
            score += evaluate_window(window, ai_piece, player_piece)
            window = [board.board[r+WIN_LENGTH-1-i][c+i] for i in range(WIN_LENGTH)]
            score += evaluate_window(window, ai_piece, player_piece)
    return score

def find_immediate_action(board, piece):
    """Uninformed Search: Finds a move that results in an immediate win."""
    for r, c in board.get_valid_locations():
        temp_board = board.copy()
        temp_board.drop_piece(r, c, piece)
        if temp_board.check_win(piece):
            return (r, c)
    return None

def minimax(board, depth, alpha, beta, maximizing_player, ai_piece, player_piece):
    """Minimax algorithm with alpha-beta pruning."""
    valid_locations = board.get_valid_locations()
    is_terminal = board.check_win(ai_piece) or board.check_win(player_piece) or board.is_draw()
    if depth == 0 or is_terminal:
        if is_terminal:
            if board.check_win(ai_piece):
                return (None, 10000000)
            elif board.check_win(player_piece):
                return (None, -10000000)
            else:
                return (None, 0)
        else:
            return (None, score_position(board, ai_piece, player_piece))
    if maximizing_player:
        value = -math.inf
        best_move = random.choice(valid_locations) if valid_locations else None
        for move in valid_locations:
            r, c = move
            temp_board = board.copy()
            temp_board.drop_piece(r, c, ai_piece)
            new_score = minimax(temp_board, depth - 1, alpha, beta, False, ai_piece, player_piece)[1]
            if new_score > value:
                value = new_score
                best_move = move
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return best_move, value
    else:  # Minimizing
        value = math.inf
        best_move = random.choice(valid_locations) if valid_locations else None
        for move in valid_locations:
            r, c = move
            temp_board = board.copy()
            temp_board.drop_piece(r, c, player_piece)
            new_score = minimax(temp_board, depth - 1, alpha, beta, True, ai_piece, player_piece)[1]
            if new_score < value:
                value = new_score
                best_move = move
            beta = min(beta, value)
            if alpha >= beta:
                break
        return best_move, value

def get_ai_move(board, ai_piece, player_piece):
    """Combines uninformed and informed search for the best move."""
    # 1. Uninformed: Check for AI's immediate winning move
    move = find_immediate_action(board, ai_piece)
    if move:
        return move
    # 2. Uninformed: Check to block player's immediate winning move
    move = find_immediate_action(board, player_piece)
    if move:
        return move
    # 3. Informed: Use Minimax for a strategic move. Depth can be increased for harder AI, but slower.
    move, _ = minimax(board, 2, -math.inf, math.inf, True, ai_piece, player_piece)
    return move

# --- Drawing Functions ---
def draw_board(board_obj):
    """Draws the grid and pieces with the new theme."""
    for c in range(COLS):
        for r in range(ROWS):
            # Draw the cell background
            pygame.draw.rect(screen, BACKGROUND_COLOR, (c * SQUARESIZE + 4, r * SQUARESIZE + SQUARESIZE + 4, SQUARESIZE - 8, SQUARESIZE - 8), border_radius=15)
            piece = board_obj.board[r][c]
            center_x = int(c * SQUARESIZE + SQUARESIZE / 2)
            center_y = int(r * SQUARESIZE + SQUARESIZE + SQUARESIZE / 2)
            if piece == 'X':
                pygame.draw.line(screen, PLAYER_X_COLOR, (center_x - RADIUS, center_y - RADIUS), (center_x + RADIUS, center_y + RADIUS), 14)
                pygame.draw.line(screen, PLAYER_X_COLOR, (center_x + RADIUS, center_y - RADIUS), (center_x - RADIUS, center_y + RADIUS), 14)
            elif piece == 'O':
                pygame.draw.circle(screen, PLAYER_O_COLOR, (center_x, center_y), RADIUS, 12)
    # Highlight winning line
    if board_obj.winner and board_obj.winning_line:
        start_pos = board_obj.winning_line[0]
        end_pos = board_obj.winning_line[-1]
        start_center_x = int(start_pos[1] * SQUARESIZE + SQUARESIZE / 2)
        start_center_y = int(start_pos[0] * SQUARESIZE + SQUARESIZE + SQUARESIZE / 2)
        end_center_x = int(end_pos[1] * SQUARESIZE + SQUARESIZE / 2)
        end_center_y = int(end_pos[0] * SQUARESIZE + SQUARESIZE + SQUARESIZE / 2)
        pygame.draw.line(screen, WIN_COLOR, (start_center_x, start_center_y), (end_center_x, end_center_y), 15)

def draw_text(text, font, color, surface, x, y, center=False):
    """Helper function to draw text."""
    textobj = font.render(text, True, color)
    textrect = textobj.get_rect()
    if center:
        textrect.center = (x, y)
    else:
        textrect.topleft = (x, y)
    surface.blit(textobj, textrect)
    return textrect

# --- Game Screens ---
def show_tutorial():
    """Displays the tutorial screen."""
    show = True
    while show:
        screen.fill(BACKGROUND_COLOR)
        draw_text('Nexus Line', myfont, HIGHLIGHT_TEXT_COLOR, screen, WIDTH / 2, 80, center=True)
        instructions = [
            "Welcome to the 6x6 Grid!",
            "",
            "1. The goal is to get 4 of your markers in a line.",
            "2. Lines can be horizontal, vertical, or diagonal.",
            "3. Take turns placing your marker in an empty square.",
            "",
            "Choose your game mode on the next screen."
        ]
        for i, line in enumerate(instructions):
            draw_text(line, tutorialfont, TEXT_COLOR, screen, WIDTH / 2, 180 + i * 40, center=True)
        draw_text('[Click anywhere to continue]', smallfont, WIN_COLOR, screen, WIDTH / 2, HEIGHT - 60, center=True)
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                show = False

def main_menu():
    """Displays the main menu with enhanced buttons."""
    while True:
        screen.fill(BACKGROUND_COLOR)
        draw_text('Main Menu', myfont, HIGHLIGHT_TEXT_COLOR, screen, WIDTH / 2, 80, center=True)
        pvp_button = pygame.Rect(WIDTH/2 - 175, 200, 350, 60)
        pvai_button = pygame.Rect(WIDTH/2 - 175, 280, 350, 60)
        mx, my = pygame.mouse.get_pos()
        # Draw PvP Button with hover effect
        color_pvp = BUTTON_HOVER_COLOR if pvp_button.collidepoint((mx, my)) else BUTTON_COLOR
        pygame.draw.rect(screen, color_pvp, pvp_button, border_radius=15)
        draw_text('Player vs Player', smallfont, TEXT_COLOR, screen, pvp_button.centerx, pvp_button.centery, center=True)
        # Draw PvAI Button with hover effect
        color_pvai = BUTTON_HOVER_COLOR if pvai_button.collidepoint((mx, my)) else BUTTON_COLOR
        pygame.draw.rect(screen, color_pvai, pvai_button, border_radius=15)
        draw_text('Player vs AI', smallfont, TEXT_COLOR, screen, pvai_button.centerx, pvai_button.centery, center=True)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if pvp_button.collidepoint((mx, my)):
                    return "PVP", 'X'
                if pvai_button.collidepoint((mx, my)):
                    chosen_piece = choose_piece()
                    return "PVAI", chosen_piece
        pygame.display.update()

def choose_piece():
    """Screen for the player to choose their marker."""
    while True:
        screen.fill(BACKGROUND_COLOR)
        draw_text('Choose Your Marker', myfont, HIGHLIGHT_TEXT_COLOR, screen, WIDTH / 2, 80, center=True)
        x_button = pygame.Rect(WIDTH/2 - 150, 200, 120, 120)
        o_button = pygame.Rect(WIDTH/2 + 30, 200, 120, 120)
        mx, my = pygame.mouse.get_pos()
        # Draw X Button
        color_x = BUTTON_HOVER_COLOR if x_button.collidepoint((mx, my)) else BUTTON_COLOR
        pygame.draw.rect(screen, color_x, x_button, border_radius=15)
        draw_text('X', pygame.font.SysFont("Segoe UI", 80, bold=True), PLAYER_X_COLOR, screen, x_button.centerx, x_button.centery, center=True)
        # Draw O Button
        color_o = BUTTON_HOVER_COLOR if o_button.collidepoint((mx, my)) else BUTTON_COLOR
        pygame.draw.rect(screen, color_o, o_button, border_radius=15)
        draw_text('O', pygame.font.SysFont("Segoe UI", 80, bold=True), PLAYER_O_COLOR, screen, o_button.centerx, o_button.centery, center=True)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if x_button.collidepoint((mx, my)):
                    return 'X'
                if o_button.collidepoint((mx, my)):
                    return 'O'
        pygame.display.update()

# --- Main Game Loop ---
def game_loop():
    """The main loop that runs the game."""
    show_tutorial()
    while True:  # Loop to allow playing again
        game_mode, player_piece_choice = main_menu()
        board = Board()
        game_over = False
        if game_mode == "PVP":
            turn = 'X'
        else:  # PVAI
            player_piece = player_piece_choice
            ai_piece = 'O' if player_piece == 'X' else 'X'
            turn = 'X'  # X always starts
        screen.fill(GRID_COLOR)
        draw_board(board)
        pygame.display.update()
        while not game_over:
            is_ai_turn = (game_mode == "PVAI" and turn == ai_piece)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN and not is_ai_turn:
                    posx, posy = event.pos
                    if posy < SQUARESIZE:
                        continue
                    col = int(math.floor(posx / SQUARESIZE))
                    row = int(math.floor((posy - SQUARESIZE) / SQUARESIZE))
                    if board.is_valid_location(row, col):
                        board.drop_piece(row, col, turn)
                        if board.check_win(turn):
                            message = f"Player {turn} wins!"
                            game_over = True
                        elif board.is_draw():
                            message = "It's a Draw!"
                            game_over = True
                        else:
                            turn = 'O' if turn == 'X' else 'X'
            if not game_over and is_ai_turn:
                pygame.draw.rect(screen, BACKGROUND_COLOR, (0, 0, WIDTH, SQUARESIZE))
                draw_text("AI is thinking...", smallfont, PLAYER_O_COLOR, screen, 20, 20)
                pygame.display.update()
                move = get_ai_move(board, ai_piece, player_piece)
                if move:
                    time.sleep(0.5)
                    board.drop_piece(move[0], move[1], ai_piece)
                    if board.check_win(ai_piece):
                        message = "AI wins!"
                        game_over = True
                    elif board.is_draw():
                        message = "It's a Draw!"
                        game_over = True
                    else:
                        turn = player_piece
                else:
                    message = "It's a Draw!"
                    game_over = True
            screen.fill(GRID_COLOR)
            draw_board(board)
            pygame.draw.rect(screen, BACKGROUND_COLOR, (0, 0, WIDTH, SQUARESIZE))
            if not game_over:
                msg = f"Player {turn}'s Turn"
                color = PLAYER_X_COLOR if turn == 'X' else PLAYER_O_COLOR
                draw_text(msg, myfont, color, screen, WIDTH / 2, SQUARESIZE / 2, center=True)
            else:
                draw_text(message, myfont, WIN_COLOR, screen, WIDTH / 2, SQUARESIZE / 2 - 10, center=True)
                draw_text("Click to play again", smallfont, TEXT_COLOR, screen, WIDTH / 2, SQUARESIZE / 2 + 30, center=True)
            pygame.display.update()

        if game_over:
            waiting = True
            while waiting:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        waiting = False
                        break

if __name__ == "__main__":
    game_loop()
