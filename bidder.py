class Bidder:
    # Attributes:
    # bid: int          bid price
    # state: State      State object attached to bid price
    # time: int         in what iteration of the period the bid was updated, -1 if before event

    def __init__(self, bid: int, state: State, time = -1):
        self.bid = bid
        self.state = state
        self.time = time
    
    # Comparison operations for max heap implementation. We reverse this because python's heapq implementation is a min heap
    # We give priority to bids that are higher and times that are lower
    def __lt__(self, other) -> bool:
        if self.bid == other.bid:
            return self.time < other.time
        return self.bid > other.bid

    def __eq__(self, other) -> bool:
        return self.bid == other.bid and self.time == other.time

    # String representation of our bidder
    def __str__(self):
        return f"({self.bid}:{self.time})"

    def resetBid(self, time: int) -> None:
        self.bid = 0
        self.state.resetBid()
        self.time = time