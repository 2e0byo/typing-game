import curses
import sys
from random import choices, randint
from time import sleep

from .score import Score
from .terminal import Terminal
from .timer import PausableMonotonic
from .word import Word

words = ("add", "subtract", "next")
weights = {k: 100 for k in words}
INPUT_LOOP_DELAY = 0.001


class Game:
    def __init__(self, words: list[str], weights: dict[str, float], terminal: Terminal):
        self.words = words
        self.weights = weights
        self.timer = PausableMonotonic()
        self.running = True
        self.terminal = terminal

    def main(self, stdscr):
        """Main loop."""
        self.terminal.stdscr = stdscr
        stdscr.clear()
        curses.curs_set(False)

        self.score = Score(self.terminal)
        self.score.display()
        max_y, max_x = stdscr.getmaxyx()
        max_y -= 2

        while self.running:
            word = choices(self.words, self.weights.values())[0]
            x = randint(0, max_x - len(word))
            word = Word(
                word, weights[word], self.terminal, x, 0, self.score, self.timer
            )

            delay = 0.1

            typed = False
            word.start = self.timer()
            for y in range(max_y):
                if y:
                    word.clear()
                word.y = y
                word.display()
                if self.input_loop(word, delay):
                    typed = True
                    break

            if word.untyped:
                weights[word.word] = word.score(self.timer())

    def input_loop(self, word: Word, delay: float):
        """Input loop in game."""
        now = start = self.timer()
        while now - start < delay:
            ch = word.scr.getch()
            if ch == 27:
                self.menu()
            if ch != -1:
                ret = word.submit(chr(ch), now)
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
        win = self.terminal.menu_win
        win.addstr(1, 2, "r", curses.A_BOLD)
        win.addstr(1, 4, " Return to Game.")
        while True:
            key = win.getkey()
            if key == "r":
                break
        del win
        self.terminal.main_win.touchwin()
        self.terminal.main_win.refresh()
        self.timer.unpause()


game = Game(words, weights, Terminal())
curses.wrapper(game.main)
