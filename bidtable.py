from heapq import heappop, heappush
from state import State

class Bidder:
    # Attributes:
    # bid: int (bid price)
    # state: State (State object attached to bid price)
    # time: int (in what iteration of event the bid was updated, 0 if before event)

    def __init__(self, bid, state, time = 0):
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

class BidTable:
    # Attributes:
    # bt: dict{state_num: List[Bidder]} (dictionary of key of state_num and value of max heap of Bidders)

    # Intialize bid table by iterating through all the states in each small world
    def __init__(self, small_worlds):
        self.bt = dict()
        for small_world in small_worlds:
            for state_num, state in small_world.states.items():
                b = Bidder(state.bid, state)
                # There already exists a heap for this state
                if self.bt.get(state_num):
                    heappush(self.bt[state_num], b)
                else:
                    self.bt[state_num] = [b]

    # String representation
    def __str__(self) -> str:
        ans = f"Bid table:\n"
        
        state_nums = sorted(self.bt.keys())
        for state_num in state_nums:
            ans += f"{state_num}: {list(map(str, self.bt[state_num]))}\n"
        return ans

    # Update our bid table by passing in the State that has been modified and time representing which iteration it was modified
    # We find the state in bt[state_num] and pop it
    # We then push a new instance of bidder onto bt[state_num]
    def updateBidder(self, state: State, time: int) -> None:
        heap = self.bt[state.state_num]
        for bidder in heap:
            if bidder.state is state:
                heap.remove(bidder)
                break
        heappush(heap, Bidder(state.bid, state, time))
                
        


