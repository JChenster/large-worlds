from heapq import heappop, heappush
from typing import List
from smallworld import SmallWorld
from state import State
from bidder import Bidder
from asker import Asker
from agentintelligence import aspirationFirstOrderAdaptive

class MarketTable:
    # Attributes:
    # table: dict{state_num: List[Bidder/Asker]}    dictionary of key of state_num and value of Bidder/Asker object
    # is_bid_table: bool                            True if this is a bid table, False if ask table

    # Intialize bid table by iterating through all the states in each small world
    # table_type must be "bid" or "ask"
    # We make the model choice that bids and asks placed earlier receive priority
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

    # Resets the bids and asks for a state to 0 and 1 respectively
    # Also updates aspiration levels via first order adaptive
    def resetState(self, other_table, state_num: int, time: int, transaction_price: float) -> None:
        for agent in self.table[state_num]:
            agent.resetBid(time) if self.is_bid_table else agent.resetAsk(time)
            agent.state.updateAspiration(aspirationFirstOrderAdaptive(agent.state.aspiration, transaction_price))
        for agent in other_table.table[state_num]:
            agent.resetBid(time) if other.is_bid_table else agent.resetAsk(time)

    # We check to see if there is a market clearing transaction ie. check to see if the lowest ask/highest bid is acceptable
    # Self and table must represent a bid and ask table together
    # Returns the price of the successful transaction, -1 if unsuccessful
    # We choose to conduct transactions at the midpoint of the bid and ask by default
    # But we can also do it by which submitted their bid/ask in the earlier iteration
    def marketMake(self, other_table, state, time: int, by_midpoint = True, by_time = False) -> float:
        if by_midpoint and by_time or not(by_midpoint or by_time):
            raise ValueError("Exactly one of by_midpoint and by_time must be True")
        
        # We peek at the lowest ask or highest bid depending on what we want
        is_bid_order = self.is_bid_table

        # peek points to the optimal Bidder/Asker object
        peek = other_table.table[state.state_num][0]
        buyer = state if is_bid_order else peek.state
        seller = peek.state if is_bid_order else state

        if buyer is seller:
            return -1
        if buyer.bid >= seller.ask:
            if by_midpoint:
                transaction_price = (buyer.bid + seller.ask) / 2
            else:
                transaction_price = peek.ask if is_bid_order else peek.bid
            # Adjust amounts and balances
            transaction_amount = seller.amount

            # Reset state bid/ask in tables
            # Update aspiration respectively
            self.resetState(self, other_table)
        else:
            self.updateTable(state, time)
            return -1