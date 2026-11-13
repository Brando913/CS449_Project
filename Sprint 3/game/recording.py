"""Plain-text recording of a game so it can be saved and replayed.

File format (one item per line):

    PEG_SOLITAIRE_RECORDING 1
    board_type=English
    size=7
    mode=manual
    move 1 3 3 3          # from_row from_col to_row to_col
    randomize PPPXX/...   # full board after a randomization (rows separated by /)
"""

MAGIC = "PEG_SOLITAIRE_RECORDING 1"
MOVE = "move"
RANDOMIZE = "randomize"


class Recording:
    def __init__(self, board_type, size, mode, events=None):
        self.board_type = board_type
        self.size = size
        self.mode = mode
        self.events = list(events or [])  # ("move", from, to) / ("randomize", rows)

    def add_move(self, frm, to):
        self.events.append((MOVE, frm, to))

    def add_randomize(self, rows):
        self.events.append((RANDOMIZE, list(rows)))

    def to_text(self):
        lines = [MAGIC, f"board_type={self.board_type}", f"size={self.size}", f"mode={self.mode}"]
        for event in self.events:
            if event[0] == MOVE:
                (r1, c1), (r2, c2) = event[1], event[2]
                lines.append(f"{MOVE} {r1} {c1} {r2} {c2}")
            else:
                lines.append(f"{RANDOMIZE} {'/'.join(event[1])}")
        return "\n".join(lines) + "\n"

    @classmethod
    def from_text(cls, text):
        lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
        if not lines or lines[0] != MAGIC:
            raise ValueError("Not a peg solitaire recording")
        header = {}
        events = []
        for ln in lines[1:]:
            if "=" in ln and not ln.startswith((MOVE, RANDOMIZE)):
                key, _, value = ln.partition("=")
                header[key] = value
                continue
            parts = ln.split()
            try:
                if parts[0] == MOVE and len(parts) == 5:
                    r1, c1, r2, c2 = map(int, parts[1:])
                    events.append((MOVE, (r1, c1), (r2, c2)))
                elif parts[0] == RANDOMIZE and len(parts) == 2:
                    events.append((RANDOMIZE, parts[1].split("/")))
                else:
                    raise ValueError
            except ValueError:
                raise ValueError(f"Bad recording line: {ln!r}") from None
        try:
            return cls(header["board_type"], int(header["size"]), header["mode"], events)
        except (KeyError, ValueError):
            raise ValueError("Recording header is missing or invalid") from None

    def save(self, path):
        with open(path, "w", encoding="utf-8") as f:
            f.write(self.to_text())

    @classmethod
    def load(cls, path):
        with open(path, encoding="utf-8") as f:
            return cls.from_text(f.read())
