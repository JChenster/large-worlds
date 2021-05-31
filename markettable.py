from heapq import heappop, heappush
from smallworld import SmallWorld
from state import State
from typing import List

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

class MarketTable:
    # Attributes:
    # table: dict{state_num: List[Bidder/Asker]}    dictionary of key of state_num and value of Bidder/Asker object
    # is_bid_table: bool                            True if this is a bid table, False if ask table

    # Intialize bid table by iterating through all the states in each small world
    # table_type must be "bid" or "ask"
    def __init__(self, small_worlds: List[SmallWorld], table_type: str):
        if table_type not in ["bid", "ask"]:
            raise ValueError("Type of table must be \"bid\" or \"ask\"")
        self.is_bid_table = table_type == "bid"

        self.table = dict()
        for small_world in small_worlds:
            for state_num, state in small_world.states.items():
                actor = Bidder(state.bid, state) if self.is_bid_table else Asker(state.ask, state)
                # There already exists a heap for this state
                if self.table.get(state_num):
                    heappush(self.table[state_num], actor)
                else:
                    self.table[state_num] = [actor]

    # String representation
    def __str__(self) -> str:
        ans = f"{'Bid' if self.is_bid_table else 'Ask'} table:\n"
        
        state_nums = sorted(self.table.keys())
        for state_num in state_nums:
            ans += f"{state_num}: {list(map(str, self.table[state_num]))}\n"
        return ans

    # Update our table by passing in the State that has been modified and time representing which iteration it was modified
    # We find the state in table[state_num] and pop it
    # We then push a new instance of Bidder/Asker onto table[state_num]
    def updateTable(self, state: State, time: int) -> None:
        heap = self.table[state.state_num]
        for actor in heap:
            if actor.state is state:
                heap.remove(actor)
                break
        if self.is_bid_table:
            heappush(heap, Bidder(state.bid, state, time))
        else:
            heappush(heap, Asker(state.ask, state, time))
                
        


