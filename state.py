class State:
    # Attributes:
    # state_num: int            the number of the state in large world
    # amount: int               the amount of state that small world has
    # aspiration: float         the aspiration level that small world assigns to this state
    # bid: float                the small world's current bid for this state
    # ask: float                the small world's current ask for this state
    # parent_world: SmallWorld  reference to small world that contains this state

    # Initialize a state with its state number and its endowment amount
    def __init__(self, parent_world, state_num: int, endowment: float):
        self.state_num = state_num
        self.amount = endowment
        self.aspiration = 0
        self.resetBidAsk()
        self.parent_world = parent_world

    def updateAspiration(self, aspiration: float) -> None:
        self.aspiration = aspiration

    # alpha is a parameter that we can modify, set at .5 by default
    def firstOrderAdaptive(self, aspiration: float, price: float, alpha = .5) -> float:
        return alpha * price + (1 - alpha) * aspiration

    # Updates bid based on price improvement rule. Returns whether or not update was made
    def updateBid(self, new_bid: float) -> bool:
        if new_bid > self.bid:
            self.bid = new_bid
        return new_bid > self.bid
    
    # Updates ask based on price improvement rule. Returns whether or not update was made
    def updateAsk(self, new_ask: float) -> bool:
        if new_ask < self.ask:
            self.ask = new_ask
        return new_ask < self.ask

    def resetBid(self) -> None:
        self.bid = 0
    
    def resetAsk(self) -> None:
        self.ask = 1

    def __str__(self):
        return f"{self.amount} of state {self.state_num}, aspiration: {self.aspiration}"
