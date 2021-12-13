from time import monotonic


class PausableMonotonic:
    """A pausable version of `time.monotonic`."""

    def __init__(self):
        self.pause_elapsed = 0
        self.paused = False
        self.pause_start = None

    def pause(self):
        self.paused = True
        self.pause_start = monotonic()

    def unpause(self):
        if not self.paused:
            return
        self.pause_elapsed += monotonic() - self.pause_start
        self.paused = False

    def __call__(self):
        if self.paused:
            raise Exception("Tried to get time from paused timer!")
        return monotonic() - self.pause_elapsed
