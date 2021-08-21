from market import Market

class MarketTable:
    # Attributes:
    # table: dict{state_num: Market}    the market for each state number
    # latest_price: float               price of latest transaction conducted in this period

    # Parameters all taken from large world
    # Create MarketTable object
    # MarketTable is a map that links a security number with its Market object
    def __init__(self, L, small_worlds: dict, by_midpoint: bool, cur, alpha: float, phi: int, epsilon: float, rep_flag: int):
        self.table = dict()
        # Create a market for each security in large world
        for state_num in L:
            self.table[state_num] = Market(by_midpoint, cur, alpha, phi, epsilon, rep_flag)
        for small_world in small_worlds.values():
            # Add all securities to the reserve bank of its respective market
            # This esentially is a storage of all participants in that market
            for state_num, state in small_world.states.items():
                self.table[state_num].reserveAdd(state)
        self.latest_price = -1
    
    def __str__(self) -> str:
        ans = "Market Table:\n"
        state_nums = sorted(list(self.table.keys()))
        for state_num in state_nums:
            ans += f"{state_num}: {str(self.table[state_num])}\n"
        return ans

    # Called at the end of a period to reset all the markets
    def tableReset(self) -> None:
        for market in self.table.values():
            market.periodReset()
        self.latest_price = -1
    
    # When a bid/ask is randomly generated, it gets passed along to the correct security market
    # It updates the latest price if a transaction was conducted
    def updateBidder(self, new_bid: float, new_bidder, time: int):
        price = self.table[new_bidder.state_num].updateBidder(new_bid, new_bidder, time)
        if price != -1:
            self.latest_price = price

    def updateAsker(self, new_ask: float, new_asker, time: int):
        price = self.table[new_asker.state_num].updateAsker(new_ask, new_asker, time)
        if price != -1:
            self.latest_price = price
    
    # Returns the last price of any transaction across all markets for the current period
    # Returns -1 if no transactions have occured at all
    def getLatestPrice(self) -> float:
        return self.latest_price

    # Get market corresponding to the one trading security state_num
    def getMarket(self, state_num) -> Market:
        return self.table[state_num]