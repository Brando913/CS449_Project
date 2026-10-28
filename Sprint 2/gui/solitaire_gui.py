import tkinter as tk

from game.board import BOARD_TYPES, EMPTY, INVALID, PEG, create_board

CELL = 60
MARGIN = 24
DEFAULT_SIZE = 7
ANIM_FRAMES = 10
ANIM_MS = 16

BG = "#1b1f3b"
PANEL = "#272c55"
ACCENT = "#ffb703"
TEXT = "#f1f1f8"
MUTED = "#9aa0c9"
ERROR = "#ff6b6b"
SUCCESS = "#6bff95"
WOOD = "#b5793a"
WOOD_EDGE = "#7a4a1d"
HOLE = "#5a3512"
MARBLE = "#3a86ff"
HINT = "#6bff95"

FONT = "Helvetica"


class SolitaireGUI:
    """Tkinter view/controller. All rules live in game.board; this only draws and forwards clicks."""

    def __init__(self, root):
        self.root = root
        root.title("Peg Solitaire")
        root.configure(bg=BG)
        self.board = None
        self.selected = None
        self.hover = None
        self.moves = 0
        self.animation = None  # (from_pos, to_pos, frame) while a jump is playing

        tk.Label(root, text="PEG SOLITAIRE", bg=BG, fg=ACCENT,
                 font=(FONT, 24, "bold")).pack(pady=(14, 2))
        tk.Label(root, text="Jump pegs over each other. Leave as few as you can!",
                 bg=BG, fg=MUTED, font=(FONT, 11)).pack()

        self.build_controls()
        self.build_stats()

        self.message_label = tk.Label(root, text="Pick a size and type, then press New Game.",
                                      bg=BG, fg=TEXT, font=(FONT, 12), wraplength=420)
        self.message_label.pack(pady=(4, 0))

        self.canvas = tk.Canvas(root, width=320, height=320, bg=BG, highlightthickness=0)
        self.canvas.pack(padx=14, pady=14)
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<Motion>", self.on_motion)
        self.canvas.bind("<Leave>", self.on_leave)
        self.draw()

    # ---- widgets -------------------------------------------------------------------------

    def make_button(self, parent, text, command, **kw):
        label = tk.Label(parent, text=text, bg=kw.get("bg", ACCENT), fg=kw.get("fg", BG),
                         font=(FONT, kw.get("size", 13), "bold"), padx=kw.get("padx", 16),
                         pady=kw.get("pady", 8), cursor="hand2")
        label.bind("<Button-1>", lambda _e: command())
        return label

    def build_controls(self):
        panel = tk.Frame(self.root, bg=PANEL, padx=14, pady=10)
        panel.pack(pady=12, padx=14, fill="x")

        tk.Label(panel, text="Board size", bg=PANEL, fg=TEXT, font=(FONT, 12)).grid(
            row=0, column=0, sticky="w")
        self.size_var = tk.StringVar(value=str(DEFAULT_SIZE))
        tk.Entry(panel, textvariable=self.size_var, width=4, justify="center",
                 font=(FONT, 14, "bold")).grid(row=0, column=1, padx=8)

        tk.Label(panel, text="Board type", bg=PANEL, fg=TEXT, font=(FONT, 12)).grid(
            row=1, column=0, sticky="w", pady=(8, 0))
        self.type_var = tk.StringVar(value="English")
        self.type_buttons = {}
        row = tk.Frame(panel, bg=PANEL)
        row.grid(row=1, column=1, columnspan=2, pady=(8, 0))
        for name in BOARD_TYPES:
            btn = self.make_button(row, name, lambda n=name: self.set_type(n),
                                   size=11, padx=10, pady=4)
            btn.pack(side="left", padx=3)
            self.type_buttons[name] = btn
        self.set_type("English")

        self.make_button(panel, "NEW GAME", self.new_game, size=14, padx=20, pady=10).grid(
            row=0, column=3, rowspan=2, padx=(20, 0))
        panel.columnconfigure(2, weight=1)

    def set_type(self, name):
        self.type_var.set(name)
        for n, btn in self.type_buttons.items():
            btn.config(bg=ACCENT if n == name else BG, fg=BG if n == name else TEXT)

    def build_stats(self):
        stats = tk.Frame(self.root, bg=BG)
        stats.pack()
        self.stat_labels = {}
        for key in ("Pegs", "Moves", "Status"):
            box = tk.Frame(stats, bg=PANEL, padx=18, pady=6)
            box.pack(side="left", padx=6)
            tk.Label(box, text=key.upper(), bg=PANEL, fg=MUTED, font=(FONT, 9, "bold")).pack()
            value = tk.Label(box, text="-", bg=PANEL, fg=TEXT, font=(FONT, 18, "bold"), width=7)
            value.pack()
            self.stat_labels[key] = value

    # ---- state ---------------------------------------------------------------------------

    def show_message(self, text, colour=TEXT):
        self.message_label.config(text=text, fg=colour)

    def update_state(self):
        if self.board is None:
            for lbl in self.stat_labels.values():
                lbl.config(text="-", fg=TEXT)
            return
        over = self.board.is_game_over()
        self.stat_labels["Pegs"].config(text=str(self.board.peg_count()))
        self.stat_labels["Moves"].config(text=str(self.moves))
        self.stat_labels["Status"].config(text="GAME OVER" if over else "Playing",
                                          fg=SUCCESS if over else TEXT)

    def new_game(self):
        if self.animation:
            return
        try:
            size = int(self.size_var.get())
        except ValueError:
            self.show_message("Board size must be a whole number.", ERROR)
            return
        try:
            board = create_board(self.type_var.get(), size)
        except ValueError as err:
            self.show_message(str(err), ERROR)
            return
        self.board = board
        self.selected = None
        self.hover = None
        self.moves = 0
        extent = 2 * MARGIN + size * CELL
        self.canvas.config(width=extent, height=extent)
        self.show_message("Game on! Click a peg, then a glowing hole to jump.")
        self.update_state()
        self.draw()

    # ---- drawing -------------------------------------------------------------------------

    def cell_box(self, pos):
        x, y = MARGIN + pos[1] * CELL, MARGIN + pos[0] * CELL
        return x, y, x + CELL, y + CELL

    def draw_marble(self, cx, cy, radius, colour, selected=False):
        if selected:
            self.canvas.create_oval(cx - radius - 6, cy - radius - 6, cx + radius + 6,
                                    cy + radius + 6, fill="", outline=ACCENT, width=4)
        self.canvas.create_oval(cx - radius + 3, cy - radius + 5, cx + radius + 3, cy + radius + 5,
                                fill="#3b2208", outline="")  # shadow
        self.canvas.create_oval(cx - radius, cy - radius, cx + radius, cy + radius,
                                fill=colour, outline="#10132b", width=2)
        self.canvas.create_oval(cx - radius * 0.55, cy - radius * 0.65, cx - radius * 0.05,
                                cy - radius * 0.2, fill="#ffffff", outline="", stipple="gray50")

    def draw(self):
        c = self.canvas
        c.delete("all")
        if self.board is None:
            c.create_text(int(c["width"]) / 2, int(c["height"]) / 2, text="🎯", font=(FONT, 60))
            return
        size = self.board.size
        hints = set()
        if self.selected is not None:
            hints = {to for frm, to in self.board.get_legal_moves() if frm == self.selected}
        moving_from = self.animation[0] if self.animation else None

        for r in range(size):
            for col in range(size):
                if self.board.get_cell(r, col) == INVALID:
                    continue
                x0, y0, x1, y1 = self.cell_box((r, col))
                c.create_rectangle(x0, y0, x1, y1, fill=WOOD, outline=WOOD_EDGE, width=2)
        for r in range(size):
            for col in range(size):
                state = self.board.get_cell(r, col)
                if state == INVALID:
                    continue
                x0, y0, x1, y1 = self.cell_box((r, col))
                cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
                c.create_oval(cx - 17, cy - 17, cx + 17, cy + 17, fill=HOLE, outline="#3b2208", width=2)
                if (r, col) in hints:
                    c.create_oval(cx - 14, cy - 14, cx + 14, cy + 14, fill="", outline=HINT, width=4)
                if state == PEG and (r, col) != moving_from:
                    lift = self.hover == (r, col) and self.animation is None
                    self.draw_marble(cx, cy - (2 if lift else 0), 24 if lift else 22,
                                     MARBLE, self.selected == (r, col))
        if self.animation:
            frm, to, frame = self.animation
            t = frame / ANIM_FRAMES
            fx, fy = [(a + b) / 2 for a, b in zip(self.cell_box(frm)[:2], self.cell_box(frm)[2:])]
            tx, ty = [(a + b) / 2 for a, b in zip(self.cell_box(to)[:2], self.cell_box(to)[2:])]
            arc = -22 * (1 - (2 * t - 1) ** 2)
            self.draw_marble(fx + (tx - fx) * t, fy + (ty - fy) * t + arc, 24, MARBLE)

    # ---- interaction ---------------------------------------------------------------------

    def pos_from_event(self, event):
        return ((event.y - MARGIN) // CELL, (event.x - MARGIN) // CELL)

    def on_motion(self, event):
        if self.board is None or self.animation:
            return
        pos = self.pos_from_event(event)
        over_peg = self.board.get_cell(*pos) == PEG
        new = pos if over_peg else None
        self.canvas.config(cursor="hand2" if over_peg else "")
        if new != self.hover:
            self.hover = new
            self.draw()

    def on_leave(self, _event):
        if self.hover is not None:
            self.hover = None
            self.draw()

    def on_click(self, event):
        if self.animation:
            return
        if self.board is None:
            self.show_message("Press NEW GAME to start.", ERROR)
            return
        if self.board.is_game_over():
            self.show_message("The game is over. Press NEW GAME to play again.", ERROR)
            return
        pos = self.pos_from_event(event)
        state = self.board.get_cell(*pos)
        if state == PEG:
            self.selected = pos
            self.show_message("Nice! Now click a glowing hole to jump.")
        elif state == EMPTY and self.selected is not None:
            if self.board.is_valid_move(self.selected, pos):
                self.start_jump(self.selected, pos)
                return
            self.show_message("Illegal move: jump over an adjacent peg into an empty hole.", ERROR)
        elif state == EMPTY:
            self.show_message("Select a peg first.", ERROR)
        self.update_state()
        self.draw()

    def start_jump(self, frm, to):
        self.animation = (frm, to, 0)
        self.step_jump()

    def step_jump(self):
        frm, to, frame = self.animation
        if frame < ANIM_FRAMES:
            self.animation = (frm, to, frame + 1)
            self.draw()
            self.root.after(ANIM_MS, self.step_jump)
            return
        self.animation = None
        self.board.make_move(frm, to)
        self.selected = None
        self.moves += 1
        if self.board.is_game_over():
            left = self.board.peg_count()
            verdict = "PERFECT! Only one peg left!" if left == 1 else f"Pegs remaining: {left}"
            self.show_message(f"Game over! No moves left. {verdict}", SUCCESS)
        else:
            self.show_message("Great jump!")
        self.update_state()
        self.draw()
