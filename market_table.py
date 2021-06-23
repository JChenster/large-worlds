from market import Market

class MarketTable:
    # Attributes:
    # table: dict{state_num: Market}    the market for each state number

    # Parameters all taken from large world
    def __init__(self, L, small_worlds: dict, by_midpoint: bool, cur, alpha: float, phi: int, epsilon: float):
        self.table = dict()
        for state_num in L:
            self.table[state_num] = Market(by_midpoint, cur, alpha, phi, epsilon)
        for small_world in small_worlds.values():
            for state_num, state in small_world.states.items():
                self.table[state_num].reserveAdd(state)
    
    def __str__(self) -> str:
        ans = "Market Table:\n"
        state_nums = sorted(list(self.table.keys()))
        for state_num in state_nums:
            ans += f"{state_num}: {str(self.table[state_num])}\n"
        return ans

    # Called at the end of a period
    def tableReset(self) -> None:
        for market in self.table.values():
            market.periodReset()
    
    def updateBidder(self, new_bid: float, new_bidder, time: int) -> bool:
        return self.table[new_bidder.state_num].updateBidder(new_bid, new_bidder, time)

    def updateAsker(self, new_ask: float, new_asker, time: int) -> bool:
        return self.table[new_asker.state_num].updateAsker(new_ask, new_asker, time)