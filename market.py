from agentintelligence import priceFirstOrderAdaptive

class Market:
    # Attributes:
    # bid: float            highest bid
    # bidder: State         State object with the highest bid
    # bidder_time: int      what iteration highest bidder made their offer in
    # ask: float            lowest ask
    # asker: State          State object with the lowest bid
    # asker_time: int       what iteration asker made their offer in
    # by_midpoint: bool     whether or not transaction prices should be the midpoint of the bid-ask spread, if False we use the price of the earlier order
    # reserve: List[State]  all State objects of the small  worlds that are participating in this market
    
    def __init__(self, by_midpoint):
        self.by_midpoint = by_midpoint
        self.reserve = []
        self.marketReset(-1)
        self.transactions = 0

    def __str__(self) -> str:
        bidder_str = self.bidder.parent_world.agent_num if self.bidder else None
        asker_str = self.asker.parent_world.agent_num if self.asker else None
        return f"({round(self.bid,2)},{bidder_str},{self.bidder_time}) - ({round(self.ask,2)},{asker_str},{self.asker_time})"
    
    # We reset all the bids and asks at the beginning of a period or after a successful transaction
    def marketReset(self, time: int) -> None:
        self.bid = 0
        self.ask = 1
        self.bidder = self.asker = None
        self.bidder_time = self.asker_time = time

    def reserveAdd(self, state) -> None:
        self.reserve.append(state)

    # We only update bidder if new bidder is higher or there is no current bidder
    # Return if update was done
    def updateBidder(self, new_bid: float, new_bidder, time: int) -> bool:
        if not self.bidder or new_bid > self.bid:
            self.bid = new_bid
            self.bidder = new_bidder
            self.bidder_time = time
            self.marketMake(time)
            return True
        return False
    
    # We only update asker if they have more than 1 in their security balance and there is no current asker or their ask is lower
    # Return if update was done
    def updateAsker(self, new_ask: float, new_asker, time: int) -> bool:
        if new_asker.amount > 0 and (not self.asker or new_ask < self.ask):
            self.ask = new_ask
            self.asker = new_asker
            self.asker_time = time
            self.marketMake(time)
            return True
        return False

    # Checks to see if there is a market clearing transaction and if there is, it conducts the trade
    def marketMake(self, time: int) -> bool:
        if not (self.bidder and self.asker) or self.bidder is self.asker or self.bid < self.ask:
            return False
        if self.by_midpoint:
            transaction_price = (self.bid + self.ask) / 2
        else:
            transaction_price = self.bid if self.bidder_time < self.asker_time else self.ask
        
        # Adjust amounts and balances
        # We sell and buy 1 unit of a security at a time
        self.asker.parent_world.balanceAdd(transaction_price)
        self.bidder.parent_world.balanceAdd(-1 * transaction_price)
        self.asker.amountAdd(-1)
        self.bidder.amountAdd(1)
        
        # Store transaction data in database
        
        # Temporary output 
        buyer_id = self.bidder.parent_world.agent_num
        seller_id = self.asker.parent_world.agent_num
        action = 1 if self.bidder_time > self.asker_time else 0
        print(f"Iteration #:{time}\tBuyer ID:{buyer_id}\tSeller ID:{seller_id}\tTransaction Price:{transaction_price}\tAction:{action}")

        # Reset the market and adjust the aspiration of our agents who are aware of this state
        self.marketReset(time)
        for state in self.reserve:
            state.updateAspiration(priceFirstOrderAdaptive(state.aspiration, transaction_price))
        return True
