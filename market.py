import agent_intelligence as ai

class Market:
    # Attributes:
    # Auction-specific
    # bid: float                highest bid
    # bidder: State             State object with the highest bid
    # bidder_time: int          what iteration highest bidder made their offer in
    # ask: float                lowest ask
    # asker: State              State object with the lowest bid
    # asker_time: int           what iteration asker made their offer in

    # Mechanism-specific
    # by_midpoint: bool         whether or not transaction prices should be the midpoint of the bid-ask spread, if False we use the price of the earlier order
    # reserve: List[State]      all State objects of the small  worlds that are participating in this market
    # cur: Cursor               Cursor object to execute database commands
    # num_transactions: int     number of transactions have been conducted in this market in this period
    # period_num: int           current period
    # alpha: float              alpha for post-transaction first order adaptive process
    # phi: int                  phi for representativeness module
    # epsilon: float            epsilon for representativeness module
    # price_history: float      list of transaction prices for this market in a period
    # price_pattern: List[int]  stores a list of 1 for increasing price, -1 for decreasing price, and 0 for same
    
    def __init__(self, by_midpoint: bool, cur, alpha: float, phi: int, epsilon: float):
        self.by_midpoint, self.cur, self.alpha, self.phi, self.epsilon = by_midpoint, cur, alpha, phi, epsilon
        self.reserve = []
        self.marketReset(-1)
        self.num_transactions = 0
        self.period_num = 0

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
        self.price_history = self.price_pattern = []

    # Reset the market at the end of a period
    def periodReset(self) -> None:
        self.marketReset(-1)
        self.num_transactions = 0
        self.period_num += 1

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
        state_num = self.bidder.state_num
        buyer_id = self.bidder.parent_world.agent_num
        seller_id = self.asker.parent_world.agent_num
        action = 1 if self.bidder_time > self.asker_time else 0
        self.cur.execute("INSERT INTO transactions VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", 
                        [self.period_num, time, state_num, self.num_transactions, buyer_id, seller_id, 
                        transaction_price, action, self.bid, self.bidder.aspiration, self.ask, self.asker.aspiration, self.bid - self.ask]
                        )

        # Reset the market and adjust the aspiration of our agents who are aware of this state
        # We will test to see if there is a string of increases or decreases that would trigger the representativeness module
        self.num_transactions += 1
        if self.price_history:
            if self.price_history[-1] < transaction_price:
                self.price_pattern.append(1)
            elif self.price_history[-1] > transaction_price:
                self.price_pattern.append(-1)
            else:
                self.price_pattern.append(0)
        self.price_history.append(transaction_price)
        pattern = ai.detectPattern(self.phi, self.price_pattern)

        for state in self.reserve:
            if state_num not in state.parent_world.not_info:
                state.updateAspiration(ai.priceFirstOrderAdaptive(state.aspiration, transaction_price, self.alpha))
                state.updateAspiration(ai.representativenessAdjustment(state.aspiration, self.epsilon, pattern))
    
        self.marketReset(time)
        return True