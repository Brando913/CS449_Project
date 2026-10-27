import tkinter as tk
from tkinter import messagebox

from game.board import BOARD_TYPES, EMPTY, INVALID, PEG, create_board

CELL = 56
MARGIN = 20
DEFAULT_SIZE = 7


class SolitaireGUI:
    """Tkinter view/controller. All rules live in game.board; this only draws and forwards clicks."""

    def __init__(self, root):
        self.root = root
        self.root.title("Peg Solitaire")
        self.board = None
        self.selected = None

        controls = tk.Frame(root)
        controls.pack(padx=10, pady=10, anchor="w")

        tk.Label(controls, text="Board size").grid(row=0, column=0, sticky="w")
        self.size_var = tk.StringVar(value=str(DEFAULT_SIZE))
        tk.Entry(controls, textvariable=self.size_var, width=4).grid(row=0, column=1, padx=5)

        tk.Label(controls, text="Board Type").grid(row=1, column=0, sticky="nw", pady=(8, 0))
        self.type_var = tk.StringVar(value="English")
        for i, name in enumerate(BOARD_TYPES):
            tk.Radiobutton(controls, text=name, variable=self.type_var, value=name).grid(
                row=1 + i, column=1, sticky="w")

        tk.Button(controls, text="New Game", command=self.new_game).grid(
            row=1, column=2, rowspan=3, padx=15)

        self.status = tk.Label(root, text="Choose a size and type, then press New Game.")
        self.status.pack()
        self.canvas = tk.Canvas(root, width=300, height=300, bg="white")
        self.canvas.pack(padx=10, pady=10)
        self.canvas.bind("<Button-1>", self.on_click)

    def new_game(self):
        try:
            size = int(self.size_var.get())
            self.board = create_board(self.type_var.get(), size)
        except ValueError as err:
            messagebox.showerror("Invalid board", str(err))
            return
        self.selected = None
        extent = 2 * MARGIN + size * CELL
        self.canvas.config(width=extent, height=extent)
        self.status.config(text=f"{self.type_var.get()} board, size {size}. Pegs: {self.board.peg_count()}")
        self.draw()

    def draw(self):
        self.canvas.delete("all")
        if self.board is None:
            return
        for r in range(self.board.size):
            for c in range(self.board.size):
                state = self.board.get_cell(r, c)
                if state == INVALID:
                    continue
                x, y = MARGIN + c * CELL, MARGIN + r * CELL
                self.canvas.create_rectangle(x, y, x + CELL, y + CELL, outline="#bbb")
                if state == PEG:
                    colour = "#e07b00" if self.selected == (r, c) else "#2a6fdb"
                    self.canvas.create_oval(x + 8, y + 8, x + CELL - 8, y + CELL - 8, fill=colour)
                elif state == EMPTY:
                    self.canvas.create_oval(x + 20, y + 20, x + CELL - 20, y + CELL - 20,
                                            fill="#ddd", outline="")

    def on_click(self, event):
        if self.board is None or self.board.is_game_over():
            return
        pos = ((event.y - MARGIN) // CELL, (event.x - MARGIN) // CELL)
        state = self.board.get_cell(*pos)
        if state == PEG:
            self.selected = pos
        elif state == EMPTY and self.selected is not None:
            if self.board.is_valid_move(self.selected, pos):
                self.board.make_move(self.selected, pos)
                self.selected = None
                self.status.config(text=f"Pegs: {self.board.peg_count()}")
                self.draw()
                if self.board.is_game_over():
                    self.end_game()
                return
            self.status.config(text="Illegal move.")
        self.draw()

    def end_game(self):
        left = self.board.peg_count()
        self.status.config(text=f"Game over. Pegs left: {left}")
        messagebox.showinfo("Game over", f"No moves left. Pegs remaining: {left}")
