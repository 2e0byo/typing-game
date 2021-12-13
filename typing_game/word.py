import curses
from time import monotonic
from functools import cached_property
from .terminal import Terminal
from .score import Score


class Word:
    def __init__(
        self,
        word: str,
        score: float,
        terminal: Terminal,
        x: int,
        y: int,
        highscore: Score,
        timer: callable = monotonic,
    ):
        self.typed = ""
        self.word = word
        self.untyped = word
        self._score = score
        self.next_char = word[0]
        self.start = None
        self.scr = terminal.main_win
        assert self.scr
        self.terminal = terminal
        self.x = x
        self.y = y
        self._len = len(word)
        self.highscore = highscore
        self.timer = timer

    @cached_property
    def typed_format(self):
        return self.terminal.colors["typed"] | curses.A_BOLD

    @cached_property
    def untyped_format(self):
        return self.terminal.colors["untyped"] | curses.A_BOLD

    def speed_multiplier(self, seconds_per_char: float):
        """A multiplier which should be slightly above 1 for fast typing and
        slightly below 1 for slow typing."""
        # return time * 1000 / len(self.typed)
        return 1

    def score(self, now):
        """Calculate weighting for word and increase highscore (if appropriate)."""
        self.clear()
        if self.untyped:
            return self._score + len(self.untyped)
        else:
            seconds = now - self.start
            multiplier = self.speed_multiplier(seconds / self._len)

            self.highscore.score(multiplier, self._len, seconds)
            return self._score / (2 * multiplier)

    def submit(self, k: str, now: float):
        """Submit k as a char in the word."""
        if k != self.next_char:
            return False

        if not self.start:
            self.start = self.timer()
        self.typed += k
        self.untyped = self.untyped[1:]
        if self.untyped:
            self.next_char = self.untyped[0]
            return None
        else:
            return self.score(now)

    def display(self):
        self.scr.addstr(self.y, self.x, self.typed, self.typed_format)
        self.scr.addstr(
            self.y,
            self.x + len(self.typed),
            self.untyped,
            self.untyped_format,
        )
        self.scr.refresh()

    def clear(self):
        self.scr.addstr(self.y, self.x, " " * self._len)
