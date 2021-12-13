from curses import curs_set, newwin, window, can_change_color, wrapper
from logging import getLogger
import curses

logger = getLogger(__name__)


class Terminal:
    """Class representing a real terminal, setup for the game."""

    def __init__(self, params: dict = None):

        colors = wrapper(lambda x: can_change_color())
        if not colors or not params:
            logger.info("Overriding colours as we are in an old terminal.")
            self.colors = dict(
                bg=curses.color_pair(0),
                untyped=curses.color_pair(1),
                typed=curses.color_pair(2),
            )

        if params:
            self.__dict__.update(params)

        self._score_win = None
        self._main_win = None
        self._menu_win = None
        self._stdscr = None

    @property
    def stdscr(self):
        if not self._stdscr:
            raise Exception("Attempt to use terminal without first setting stdscr.")
        return self._stdscr

    @stdscr.setter
    def stdscr(self, screen: window):
        self._stdscr = screen

    @property
    def score_win(self):
        if not self._score_win:
            _, width = self.stdscr.getmaxyx()
            win = newwin(1, width, 0, 0)
            win.bkgd(self.colors["bg"] | curses.A_REVERSE | curses.A_BOLD)
            self._score_win = win
        return self._score_win

    @property
    def main_win(self):
        if not self._main_win:
            max_y, max_x = self.stdscr.getmaxyx()
            max_y -= 2
            win = newwin(max_y, max_x, 2, 0)
            win.bkgd(self.colors["bg"])
            win.nodelay(True)
            self._main_win = win
        return self._main_win

    @property
    def menu_win(self):
        max_y, max_x = self.stdscr.getmaxyx()
        win = newwin(10, 40, max_y // 2 - 5, max_x // 2 - 20)
        win.bkgd(self.colors["bg"])
        win.box()
        return win
