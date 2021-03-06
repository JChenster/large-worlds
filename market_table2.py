from market2 import Market2

class MarketTable2:
    # Attributes:
    # table: dict{state_num: Market}    the market for each state number

    # Parameters all taken from large world
    # Create MarketTable object
    # MarketTable is a map that links a security number with its Market object
    def __init__(self, L, small_worlds: dict, by_midpoint: bool, cur, alpha: float):
        self.table = {}
        # Create a market for each security in large world
        for state_num in L:
            self.table[state_num] = Market2(by_midpoint, cur, alpha)
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
    def updateBidder(self, new_bid: float, new_bidder, time: int):
        price = self.table[new_bidder.state_num].updateBidder(new_bid, new_bidder, time)

    def updateAsker(self, new_ask: float, new_asker, time: int):
        price = self.table[new_asker.state_num].updateAsker(new_ask, new_asker, time)
    
    # Attempts to create a market clearing transaction for each of the markets in the table
    # Called at the end of an iteration
    def tableMarketMake(self, iteration_num: int) -> None:
        for market in self.table.values():
            market.marketMake(iteration_num)

    # Returns the minimum price for the market of state_num
    def getMarketMinPrice(self, state_num: int) -> float:
        return self.table[state_num].getMinPrice()

    # Get market corresponding to the one trading security state_num
    def getMarket(self, state_num) -> Market2:
        return self.table[state_num]