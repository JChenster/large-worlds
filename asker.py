class Asker:
    # Attributes
    # ask: int          ask price
    # state: State      State object attached to ask price
    # time: int         in what iteration of the period the ask was updated, -1 if before event
    def __init__(self, ask: int, state: State, time = -1):
        self.ask = ask
        self.state = state
        self.time = time
    
    # Comparison operations for min heap implementation
    # We give priority to asks that are lower and times that are lower
    def __lt__(self, other) -> bool:
        if self.ask == other.ask:
            return self.time < other.time
        return self.ask < other.ask

    def __eq__(self, other) -> bool:
        return self.ask == other.ask and self.time == other.time

    # String representation of our asker
    def __str__(self):
        return f"({self.ask}:{self.time})"

    def resetAsk(self, time: int) -> None:
        self.ask = 1
        self.state.resetAsk()
        self.time = time