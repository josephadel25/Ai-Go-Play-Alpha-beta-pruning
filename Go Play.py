import tkinter as tk
from tkinter import messagebox

captured_WhiteStones = 0
captured_BlackStones = 0
directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
goodPlays = [(3, 3), (3, 5)]


def create_board():
    return [[{'content': ' ', 'score': 0} for _ in range(19)] for _ in range(19)]


def is_valid_position(board, row, col):
    return 0 <= row < len(board) and 0 <= col < len(board[0])


def apply_move(board, move, player):
    row, col = move
    board[row][col]['content'] = player


def undo_move(board, move):
    row, col = move
    board[row][col]['content'] = ' '


def has_liberty(board, row, col):
    player = board[row][col]['content']
    visited = set()


    def dfs(r, c):
        if (r, c) in visited:
            return
        visited.add((r, c))

        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            if is_valid_position(board, nr, nc) and board[nr][nc]['content'] == player:
                dfs(nr, nc)

    dfs(row, col)


    for r, c in visited:
        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            if is_valid_position(board, nr, nc):
                if board[nr][nc]['content'] == ' ':
                    return True
    return False


def get_liberties(board, r, c):
    player = board[r][c]['content']
    liberty_index = []
    visited = set()

    def dfs(r, c):
        if (r, c) in visited:
            return False
        visited.add((r, c))

        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            if is_valid_position(board, nr, nc):
                if board[nr][nc]['content'] == ' ':
                    liberty_index.append((nr, nc))

        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            if is_valid_position(board, nr, nc):
                if board[nr][nc]['content'] == player:
                    dfs(nr, nc)
        return False

    dfs(r, c)
    return liberty_index


def get_possible_moves(board):
    moves = []
    for r in range(len(board)):
        for c in range(len(board[r])):
            if (board[r][c]['content'] == ' ' and has_liberty(board,r,c)) or (board[r][c]['content']== ' ' and board[r][c]['score']==19):
                moves.append((r, c))
    return moves


def group(board, row, col):
    player = board[row][col]['content']
    group_list = []
    visited = set()

    def dfs(r, c):
        if (r, c) in visited:
            return
        visited.add((r, c))
        group_list.append((r, c))
        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            if is_valid_position(board, nr, nc):
                if board[nr][nc]['content'] == ' ':
                    return
                if board[nr][nc]['content'] == player:
                    dfs(nr, nc)

    dfs(row, col)

    for r, c in group_list:
        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            if is_valid_position(board, nr, nc) and board[nr][nc]['content'] == ' ':
                return []
    return group_list


def capture(board, r, c, current_player):
    global captured_WhiteStones
    global captured_BlackStones
    opponent = 'W' if current_player == 'B' else 'B'
    for dr, dc in directions:
        nr, nc = r + dr, c + dc

        if 0 <= nr < len(board) and 0 <= nc < len(board[0]):
            if board[nr][nc]['content'] == opponent and not has_liberty(board, nr, nc):
                Group = group(board, nr, nc)
                if opponent == 'W':
                    captured_WhiteStones += len(Group)
                else:
                    captured_BlackStones += len(Group)
                for gr, gc in Group:
                    board[gr][gc]['content'] = ' '


def alpha_beta(board, depth, alpha, beta, maximizing_player):
    best_move = None
    possible_moves = get_possible_moves(board)

    if depth == 0 or not possible_moves:
        return None, evaluate_board(board)

    max_score = max(board[r][c]['score'] for r, c in possible_moves)
    best_moves = [(r, c) for r, c in possible_moves if board[r][c]['score'] == max_score]

    if maximizing_player:
        max_eval = -float('inf')
        for move in best_moves:
            apply_move(board, move, 'W')
            huristic(board)
            #huristic2(board)  #to switch active this and dactive the other one
            _, eval = alpha_beta(board, depth - 1, alpha, beta, False)
            undo_move(board, move)
            if eval > max_eval:
                max_eval = eval
                best_move = move
            alpha = max(alpha, eval)
            if beta <= alpha:
                break
        return best_move, max_eval
    else:
        min_eval = float('inf')
        for move in best_moves:
            apply_move(board, move, 'B')
            huristic(board)
            #huristic2(board)   #to switch active this and dactive the other one
            _, eval = alpha_beta(board, depth - 1, alpha, beta, True)
            undo_move(board, move)

            if eval < min_eval:
                min_eval = eval
                best_move = move
            beta = min(beta, eval)
            if beta <= alpha:
                break
        return best_move, min_eval


def minimax(board, depth, maximizing_player):
    best_move = None
    possible_moves = get_possible_moves(board)

    if depth == 0 or not possible_moves:
        return None, evaluate_board(board)

    max_score = max(board[r][c]['score'] for r, c in possible_moves)
    best_moves = [(r, c) for r, c in possible_moves if board[r][c]['score'] == max_score]

    if maximizing_player:
        max_eval = -float('inf')
        for move in best_moves:
            apply_move(board, move, 'W')
            huristic(board)
            #huristic2(board)   #to switch active this and dactive the other one
            _, eval = minimax(board, depth - 1, False)
            undo_move(board, move)
            if eval > max_eval:
                max_eval = eval
                best_move = move
        return best_move, max_eval
    else:
        min_eval = float('inf')
        for move in best_moves:
            apply_move(board, move, 'B')
            huristic(board)
            #huristic2(board)   #to switch active this and dactive the other one
            _, eval = minimax(board, depth - 1, True)
            undo_move(board, move)
            if eval < min_eval:
                min_eval = eval
                best_move = move
        return best_move, min_eval



def evaluate_board(board):

    white_territory = 0
    black_territory = 0
    visited = set()

    def explore_territory(r, c):

        queue = [(r, c)]
        territory = set()
        surrounding_colors = set()

        while queue:
            x, y = queue.pop(0)
            if (x, y) in visited:
                continue

            visited.add((x, y))
            territory.add((x, y))

            for dr, dc in directions:
                nr, nc = x + dr, y + dc
                if is_valid_position(board, nr, nc):
                    if board[nr][nc]['content'] == ' ' and (nr, nc) not in visited:
                        queue.append((nr, nc))
                    elif board[nr][nc]['content'] in {'W', 'B'}:
                        surrounding_colors.add(board[nr][nc]['content'])


        if len(surrounding_colors) == 1:
            owner = surrounding_colors.pop()
            if owner == 'W':
                return len(territory), 0
            elif owner == 'B':
                return 0, len(territory)

        return 0, 0


    for r in range(len(board)):
        for c in range(len(board[r])):
            if board[r][c]['content'] == ' ' and (r, c) not in visited:
                w_territory, b_territory = explore_territory(r, c)
                white_territory += w_territory
                black_territory += b_territory


    return (white_territory - black_territory)+(captured_BlackStones-captured_WhiteStones+6.5)


def huristic(board):
    ai_player = 'W'
    human_player = 'B'
    for r in range(len(board)):
        for c in range(len(board[r])):

            if board[r][c]['content'] == ai_player:
                liberties = get_liberties(board, r, c)
                match len(liberties):
                    case 1:
                        r,c=liberties[0]
                        board[r][c]['score'] = 35

            elif board[r][c]['content'] == human_player:
                liberties = get_liberties(board, r, c)
                match len(liberties):
                    case 4:
                        for row, col in liberties:
                            if board[row][col]['score'] < 5:
                                board[row][col]['score'] = 5
                    case 3:
                        for row, col in liberties:
                            if board[row][col]['score'] < 6:
                                board[row][col]['score'] = 6
                    case 2:
                        for row, col in liberties:
                            if board[row][col]['score'] < 7:
                                board[row][col]['score'] = 7
                    case 1:
                        for row, col in liberties:
                            if board[row][col]['score'] < 19:
                                board[row][col]['score'] = 19
                    case _:
                        for row, col in liberties:
                            if board[row][col]['score'] < 3:
                                board[row][col]['score'] = 3


def huristic2(board):
    ai_player = 'W'
    huristic(board)
    for r,c in goodPlays:
            if board[r][c]['content'] == ' ':
                board[r][c]['score'] = 30
            if board[r][c]['content'] == ai_player:
                sc=c
                sr=r
                while sc>=0:
                    if board[r][sc]['score'] < 8:
                        board[r][sc]['score'] = 8
                    sc-=1
                while sr>=0:
                    if board[sr][c]['score'] < 8:
                        board[sr][c]['score']=8
                    sr-=1


def update_all_scores(board, new_score):
    for r in range(len(board)):
        for c in range(len(board[r])):
            board[r][c]['score'] = new_score


def Go_play():
    def handle_click(event):
        nonlocal current_player
        col = round((event.x - padding) / cell_size)
        row = round((event.y - padding) / cell_size)

        if not is_valid_position(board, row, col):
            return

        if board[row][col]['content'] == ' ':
            apply_move(board, (row, col), current_player)
            capture(board, row, col, current_player)
            huristic(board)
            update_canvas()

            if not has_liberty(board, row, col):
                messagebox.showerror("Invalid Move", "Move has no liberties! Try again.")
                undo_move(board, (row, col))
                update_canvas()
                return

            current_player = 'W' if current_player == 'B' else 'B'
            if current_player == 'W':
                ai_move()

    def ai_move():
        nonlocal current_player
        best_move, _ = alpha_beta(board, 2, float('-inf'), float('inf'), True)
        if best_move:
            apply_move(board, best_move, 'W')
            capture(board, best_move[0], best_move[1], 'W')
            huristic(board)
            update_canvas()
            update_score_display()
            current_player = 'B'
            update_all_scores(board, 0)

    def update_canvas():
        canvas.delete("stone")

        for r in range(19):
            for c in range(19):
                x = padding + c * cell_size
                y = padding + r * cell_size
                content = board[r][c]['content']

                if content == 'B':
                    canvas.create_oval(x - stone_radius, y - stone_radius, x + stone_radius, y + stone_radius,
                                       fill="black", tags="stone")
                elif content == 'W':
                    canvas.create_oval(x - stone_radius, y - stone_radius, x + stone_radius, y + stone_radius,
                                       fill="white", tags="stone")

    def update_score_display():
        evaluation = evaluate_board(board)
        score_label.config(text=f"Evaluation Score: {evaluation:.1f}")
        white_captures_label.config(text=f"Captured White Stones: {captured_WhiteStones}")
        black_captures_label.config(text=f"Captured Black Stones: {captured_BlackStones}")

    # Board constants
    board = create_board()
    current_player = 'B'

    root = tk.Tk()
    root.title("Go Play")

    canvas_size = 760
    padding = 20
    cell_size = (canvas_size - 2 * padding) // 18
    stone_radius = cell_size // 2 - 2

    canvas = tk.Canvas(root, width=canvas_size, height=canvas_size, bg="#D1A76E")
    canvas.grid(row=0, column=0, columnspan=3)
    canvas.bind("<Button-1>", handle_click)

    # Draw the board lines (intersections)
    for i in range(19):
        x = padding + i * cell_size
        canvas.create_line(x, padding, x, canvas_size - padding)
        canvas.create_line(padding, x, canvas_size - padding, x)

    # Star points (hoshi) on standard Go board
    hoshi_points = [(3, 3), (3, 9), (3, 15),
                    (9, 3), (9, 9), (9, 15),
                    (15, 3), (15, 9), (15, 15)]
    for r, c in hoshi_points:
        x = padding + c * cell_size
        y = padding + r * cell_size
        canvas.create_oval(x - 3, y - 3, x + 3, y + 3, fill="black")

    # Score display
    score_label = tk.Label(root, text="Evaluation Score: 0.0", font=("Helvetica", 12))
    score_label.grid(row=1, column=0, padx=5, pady=10)

    white_captures_label = tk.Label(root, text="Captured White Stones: 0", font=("Helvetica", 12))
    white_captures_label.grid(row=1, column=1, padx=5, pady=10)

    black_captures_label = tk.Label(root, text="Captured Black Stones: 0", font=("Helvetica", 12))
    black_captures_label.grid(row=1, column=2, padx=5, pady=10)

    root.mainloop()



if __name__ == "__main__":
    Go_play()
