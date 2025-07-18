import tkinter as tk
from tkinter import messagebox
import random
import time
import heapq
import itertools
import threading

GOAL_STATE = list(range(1, 16)) + [' ']  # ✅ Correct: total 16 tiles

class PuzzleGame:
    def __init__(self, root):
        self.root = root
        self.root.title("15 Puzzle Game")
        self.tiles = GOAL_STATE[:]  # placeholder until shuffle
        self.buttons = []
        self.moves = 0
        self.start_time = None

        self.timer_label = tk.Label(self.root, text="Time: 0s", font=("Arial", 14))
        self.moves_label = tk.Label(self.root, text="Moves: 0", font=("Arial", 14))
        #self.hint_button = tk.Button(self.root, text="Hint", command=self.show_hint)

        self.create_widgets()
        self.shuffle_puzzle()

    def create_widgets(self):
        self.timer_label.grid(row=0, column=0, columnspan=2, pady=5)
        self.moves_label.grid(row=0, column=2, columnspan=1, pady=5)
        #self.hint_button.grid(row=0, column=3, pady=5)

        for i in range(4):
            row = []
            for j in range(4):
                btn = tk.Button(self.root, text="", font=("Arial", 20), width=4, height=2,
                                command=lambda i=i, j=j: self.tile_click(i, j))
                btn.grid(row=i+1, column=j, padx=2, pady=2)
                row.append(btn)
            self.buttons.append(row)

    def shuffle_puzzle(self):
        while True:
            candidate = list(range(1, 16)) + [' ']  # ✅ 16 elements
            random.shuffle(candidate)
            if self.is_solvable(candidate):
                self.tiles = candidate
                break

        if len(self.tiles) != 16:
            print("❌ Error: tiles length =", len(self.tiles))
        else:
            print("✅ Shuffled tiles:", self.tiles)

        self.moves = 0
        self.start_time = time.time()
        self.update_timer()
        self.update_gui()

    def is_solvable(self, tiles):
        nums = [x for x in tiles if x != ' ']
        inversions = 0
        for i in range(len(nums)):
            for j in range(i + 1, len(nums)):
                if nums[i] > nums[j]:
                    inversions += 1
        blank_row = tiles.index(' ') // 4
        return (inversions + (3 - blank_row)) % 2 == 0

    def update_gui(self):
        if len(self.tiles) != 16:
            print("❌ Error: self.tiles length is", len(self.tiles))
            return

        for i in range(4):
            for j in range(4):
                value = self.tiles[i * 4 + j]
                self.buttons[i][j].config(text=str(value) if value != ' ' else "")

    def tile_click(self, i, j):
        blank_index = self.tiles.index(' ')
        bi, bj = divmod(blank_index, 4)
        if abs(bi - i) + abs(bj - j) == 1:
            self.tiles[blank_index], self.tiles[i * 4 + j] = self.tiles[i * 4 + j], self.tiles[blank_index]
            self.moves += 1
            self.moves_label.config(text=f"Moves: {self.moves}")
            self.update_gui()
            if self.is_solved():
                elapsed = int(time.time() - self.start_time)
                messagebox.showinfo("Congratulations", f"You solved the puzzle in {self.moves} moves and {elapsed} seconds!")
                self.shuffle_puzzle()

    def is_solved(self):
        return self.tiles == GOAL_STATE

    def update_timer(self):
        if self.start_time:
            elapsed = int(time.time() - self.start_time)
            self.timer_label.config(text=f"Time: {elapsed}s")
        self.root.after(1000, self.update_timer)

    def show_hint(self):
        def run_solver():
            next_move = self.solve_hint(self.tiles)
            def apply_hint():
                if next_move:
                    idx_blank = self.tiles.index(' ')
                    idx_move = self.tiles.index(next_move)
                    self.tiles[idx_blank], self.tiles[idx_move] = self.tiles[idx_move], self.tiles[idx_blank]
                    self.moves += 1
                    self.moves_label.config(text=f"Moves: {self.moves}")
                    self.update_gui()
                else:
                    messagebox.showinfo("Hint", "Already solved!")
            self.root.after(0, apply_hint)
        threading.Thread(target=run_solver, daemon=True).start()

    def solve_hint(self, start):
        def heuristic(state):
            total = 0
            for i, val in enumerate(state):
                if val == ' ':
                    continue
                correct_index = GOAL_STATE.index(val)
                x1, y1 = divmod(i, 4)
                x2, y2 = divmod(correct_index, 4)
                total += abs(x1 - x2) + abs(y1 - y2)
            return total

        def get_neighbors(state):
            neighbors = []
            idx = state.index(' ')
            x, y = divmod(idx, 4)
            directions = [(-1,0), (1,0), (0,-1), (0,1)]
            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                if 0 <= nx < 4 and 0 <= ny < 4:
                    new_idx = nx * 4 + ny
                    new_state = state[:]
                    new_state[idx], new_state[new_idx] = new_state[new_idx], new_state[idx]
                    neighbors.append((new_state, new_state[idx]))
            return neighbors

        visited = set()
        counter = itertools.count()  # Unique sequence count
        queue = [(heuristic(start), 0, next(counter), start, [])]
        while queue:
            est, cost, _, state, path = heapq.heappop(queue)
            state_tuple = tuple(state)
            if state == GOAL_STATE:
                return path[0] if path else None
            if state_tuple in visited:
                continue
            visited.add(state_tuple)
            for neighbor, moved_tile in get_neighbors(state):
                heapq.heappush(
                    queue,
                    (cost + 1 + heuristic(neighbor), cost + 1, next(counter), neighbor, path + [moved_tile])
                )
        return None

# Launch the game
if __name__ == "__main__":
    root = tk.Tk()
    game = PuzzleGame(root)
    root.mainloop()
