import csv
import curses
import sys
from appdirs import AppDirs
from random import choices, randint
from time import sleep
from pathlib import Path
from datetime import datetime

from .score import Score
from .terminal import Terminal
from .timer import PausableMonotonic
from .word import Word

words = ("add", "subtract", "next")
weights = {k: 100 for k in words}
INPUT_LOOP_DELAY = 0.001


class Game:
    def __init__(
        self,
        words: list[str],
        weights: dict[str, float],
        terminal: Terminal,
        user,
    ):
        self.words = words
        self.weights = weights
        self.timer = PausableMonotonic()
        self.running = True
        self.terminal = terminal
        self.initial_delay = 0.5
        self.initial_new_word_pause = 3
        self.AppDirs = AppDirs("typing-game", "JohnMorris")
        self.user = user
        self.load_highscores()

    @property
    def delay(self):
        return self.initial_delay / (self.score.level + 1)

    @property
    def new_word_pause(self):
        return self.initial_new_word_pause / (self.score.level + 1)

    def draw_word(self):
        _, max_x = self.terminal.main_win.getmaxyx()
        word = choices(self.words, self.weights.values())[0]
        x = randint(0, max_x - len(word) - 1)
        word = Word(word, weights[word], self.terminal, x, 0, self.score, self.timer)
        return word

    def main(self, stdscr):
        """Main loop."""
        self.terminal.stdscr = stdscr
        stdscr.clear()

        curses.use_default_colors()
        for i in range(0, curses.COLORS):
            curses.init_pair(i, i, -1)
        curses.curs_set(False)

        self.score = Score(self.terminal)
        self.score.display()
        max_y, max_x = self.terminal.main_win.getmaxyx()
        max_y -= 1

        words = []
        selected = False
        start = self.timer()
        word = None

        while self.running:
            now = self.timer()
            if not words or now - start > self.new_word_pause:
                words.append(self.draw_word())
                start = now

            for w in words:
                if w.y:
                    w.clear()
                w.y += 1
                w.display()
                if w.y == max_y:
                    weights[w.word] = w.score(self.timer())
                    try:
                        words.remove(w)
                        if word is w:
                            selected = False
                    except ValueError:
                        pass

            if not selected:
                word = self.select_word(words)
                if not word:
                    continue
                selected = True

            if self.input_loop(word):
                try:
                    words.remove(word)
                except ValueError:
                    continue
                selected = False

    def getch(self):
        ch = self.terminal.main_win.getch()
        if ch == 27:
            self.menu()
            return -1
        else:
            return ch

    def select_word(self, words):
        """Get word to type."""
        now = start = self.timer()
        scr = self.terminal.main_win
        while now - start < self.delay:
            ch = self.getch()
            if ch != -1:
                k = chr(ch)
                for word in words:
                    if word.next_char == k:
                        if not self.score.start_time:
                            self.score.start_time = now
                        word.submit(k)
                        return word
            now = self.timer()

        return None

    def input_loop(self, word: Word):
        """Input loop in game."""
        now = start = self.timer()
        while now - start < self.delay:
            ch = self.getch()
            if ch != -1:
                ret = word.submit(chr(ch))
                word.display()
                if ret is not False:
                    word.display()

                if ret:
                    word.clear()
                    weights[word.word] = ret
                    return True

            sleep(INPUT_LOOP_DELAY)
            now = self.timer()

        return False

    def menu(self):
        self.timer.pause()
        options = {
            "r": ("Return to Game", None),
            "q": ("Quit", self.quit),
        }

        win = self.terminal.menu_win
        for row, (key, (text, fn)) in enumerate(options.items()):
            win.addstr(row + 1, 2, key, curses.A_BOLD)
            win.addstr(row + 1, 4, text)

        win.addstr(row + 2, 1, str(self.highscoresf))
        while True:
            key = win.getkey()
            entry = options.get(key)
            if entry:
                fn = entry[1]
                if fn:
                    fn()
                else:
                    break
        del win
        self.terminal.main_win.touchwin()
        self.terminal.main_win.refresh()
        self.timer.unpause()

    @property
    def highscoresf(self):
        d = Path(self.AppDirs.user_data_dir)
        d.mkdir(exist_ok=True)
        return d / "highscores.csv"

    def load_highscores(self):
        try:
            with self.highscoresf.open("r") as f:
                self._highscores = list(csv.DictReader(f))
        except Exception:
            self._highscores = []

    def highscores(self, user):
        return [x for x in self._highscores if x["User"] == user]

    def save_highscores(self):
        with self.highscoresf.open("w") as f:
            writer = csv.DictWriter(f, fieldnames=("User", "Date", "Score"))
            writer.writeheader()
            writer.writerows(self._highscores)

    def quit(self):
        self._highscores.append(
            dict(
                User=self.user,
                Date=datetime.now().isoformat(),
                Score=self.score.current_score,
            )
        )
        self.save_highscores()
        sys.exit()


game = Game(words, weights, Terminal(), user="Emma")
curses.wrapper(game.main)
