from .terminal import Terminal


class Score:
    HEADER = "   ESC for menu"
    AVG_WORD_LEN = 5

    def __init__(self, terminal: Terminal):
        self._score = 0.0
        # get win here
        win = terminal.score_win
        win.addstr(self.HEADER)
        win.refresh()
        self.scr = win
        self.fast = 1000
        self.seconds = 0
        self.chars = 0
        self.start_time = 0
        self.elapsed = 0

    def wpm(self, chars=None, seconds=None) -> float:
        chars = chars or self.chars
        seconds = seconds or self.elapsed - self.start_time
        words = chars / self.AVG_WORD_LEN
        return 0.0 if not chars else words / (seconds / 60)

    def set_fast(self):
        """Set `fast` threshold as 150% of current wpm."""
        self.fast = self.wpm() * 1.5

    def speed_multiplier(self, seconds: float, chars: int):
        """A multiplier which should be slightly above 1 for fast typing and
        slightly below 1 for slow typing."""
        wpm = self.wpm()
        return max(min(self.wpm(chars, seconds) / wpm, 1.5), 0.5) if wpm else 1

    def score(self, multiplier: float, chars: int, seconds: float, now: float):
        old_wpm = self.wpm()
        self.chars += chars
        self.seconds += seconds
        self.elapsed = now
        if old_wpm and abs(self.wpm() - old_wpm) / old_wpm > 0.1:
            self.set_fast()

        self._score += multiplier * chars * 10 * (self.fast / self.wpm(chars, seconds))
        self.display()

    def display(self):
        _, width = self.scr.getmaxyx()
        self.scr.addstr(0, (width // 2) - 7, f"{round(self.wpm()):>3} WPM")
        # self.scr.addstr(0, 20, f"c: {self.chars}, s: {self.seconds}")
        self.scr.addstr(
            0,
            width - len(self.HEADER) - 11,
            f"Current Score: {round(self._score):>8}",
        )
        self.scr.refresh()

    @property
    def level(self):
        return self._score // 1_000
