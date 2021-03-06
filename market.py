import agent_intelligence as ai

class Market:
    # Attributes:
    # Auction-specific
    # bid: float                    highest bid
    # bidder: State                 State object with the highest bid
    # bidder_time: int              what iteration highest bidder made their offer in
    # ask: float                    lowest ask
    # asker: State                  State object with the lowest bid
    # asker_time: int               what iteration asker made their offer in

    # Mechanism-specific
    # by_midpoint: bool             whether or not transaction prices should be the midpoint of the bid-ask spread, if False we use the price of the earlier order
    # reserve: List[State]          all State objects of the small  worlds that are participating in this market
    # cur: Cursor                   Cursor object to execute database commands
    # num_transactions: int         number of transactions have been conducted in this market in this period
    # period_num: int               current period
    # alpha: float                  alpha for post-transaction first order adaptive process
    # phi: int                      phi for representativeness module
    # epsilon: float                epsilon for representativeness module
    # rep_flag: int                 what representativeness module to use
    # price_history: List[float]    list of transaction prices for this market in a period
    # price_pattern: List[int]      stores a list of 1 for increasing price, -1 for decreasing price, and 0 for same

    # A Market object is created which represents the market for a particular security
    def __init__(self, by_midpoint: bool, cur, alpha: float, phi: int, epsilon: float, rep_flag: int):
        self.cur = cur
        self.by_midpoint, self.alpha, self.phi, self.epsilon, self.rep_flag = by_midpoint, alpha, phi, epsilon, rep_flag
        self.reserve = []

        # Initialize period as -1 becuase it will be incremented to 0 once period reset function is called
        self.period_num = -1
        self.periodReset()

    def __str__(self) -> str:
        bidder_str = self.bidder.parent_world.agent_num if self.bidder else None
        asker_str = self.asker.parent_world.agent_num if self.asker else None
        return f"({round(self.bid,2)},{bidder_str},{self.bidder_time}) - ({round(self.ask,2)},{asker_str},{self.asker_time})"
    
    # Reset all the bids and asks at the beginning of a period or after a successful transaction
    def marketReset(self, time: int) -> None:
        self.bid = 0
        self.ask = 1
        self.bidder = None
        self.asker = None
        self.bidder_time = time
        self.asker_time = time

    # Reset the market at the end of a period by resetting attributes specific to a particular period
    def periodReset(self) -> None:
        self.marketReset(-1)
        self.num_transactions = 0
        self.period_num += 1
        self.price_history = []
        self.price_pattern = []

    def reserveAdd(self, state) -> None:
        self.reserve.append(state)

    # Only update bidder if new bidder is higher or there is no current bidder
    # Returns transaction price if market clearing transaction was conducted, -1 otherwise
    def updateBidder(self, new_bid: float, new_bidder, time: int) -> bool:
        if not self.bidder or new_bid > self.bid:
            self.bid = new_bid
            self.bidder = new_bidder
            self.bidder_time = time
            # Check to see if this new bid enables a market transaction
            return self.marketMake(time)
        return -1
    
    # Only update asker if they have more than 1 in their security balance and there is no current asker or their ask is lower
    # Returns transaction price if market clearing transaction was conducted, -1 otherwise
    def updateAsker(self, new_ask: float, new_asker, time: int) -> bool:
        if new_asker.amount > 0 and (not self.asker or new_ask < self.ask):
            self.ask = new_ask
            self.asker = new_asker
            self.asker_time = time
            # Check to see if this new bid enables a market transaction
            return self.marketMake(time)
        return -1

    # Checks to see if there is a market clearing transaction and if there is, it conducts the trade
    # Returns either the price of the transaction or -1 to signify no transaction was conducted
    def marketMake(self, time: int) -> bool:
        # There is not a market clearing transaction
        if not (self.bidder and self.asker) or self.bidder is self.asker or self.bid < self.ask:
            return -1
        # Determine transaction price
        if self.by_midpoint:
            transaction_price = (self.bid + self.ask) / 2
        else:
            transaction_price = self.bid if self.bidder_time < self.asker_time else self.ask
            
        # Adjust security amounts and balances
        # Only sell and buy 1 unit of a security at a time
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
        # Test to see if there is a string of increases or decreases that would trigger the representativeness module
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

        # Apply necessary changes to all participants in this market for this security
        for state in self.reserve:
            if state_num not in state.parent_world.not_info:
                # Enact
                state.updateAspiration(ai.priceFirstOrderAdaptive(state.aspiration, transaction_price, self.alpha))
                # 2 choices of the representativeness module
                if self.rep_flag == 1:
                    state.updateAspiration(ai.representativenessAdjustment1(state, self.epsilon, pattern))
                elif self.rep_flag == 2:
                    state.updateAspiration(ai.representativenessAdjustment2(state, self.epsilon, pattern))
    
        # Reset the market after a successful transaction
        self.marketReset(time)
        return transaction_price