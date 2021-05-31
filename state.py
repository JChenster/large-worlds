class State:
    # Attributes:
    # state_num: int        the number of the state in large world
    # amount: int           the amount of state that small world has
    # aspiration: float     the aspiration level that small world assigns to this state
    # bid: float            the small world's current bid for this state
    # ask: float            the small world's current ask for this state

    # Initialize a state with its state number and its endowment amount
    def __init__(self, state_num: int, endowment: float):
        self.state_num = state_num
        self.amount = endowment
        self.aspiration = self.bid = 0
        self.ask = 1

    def updateAspiration(self, aspiration: float) -> None:
        self.aspiration = aspiration

    def firstOrderAdaptive(self, aspiration: float, price: float) -> float:
        pass

    # Updates bid based on price improvement rule. Returns whether or not update was made
    def updateBid(self, newbid: float) -> bool:
        if newbid > self.bid:
            self.bid = newbid
    
    # Updates ask based on price improvement rule. Returns whether or not update was made
    def updateAsk(self, newask: float) -> bool:
        if newask < self.ask:
            self.ask = newask 

    def __str__(self):
        return f"{self.amount} of state {self.state_num}, aspiration: {self.aspiration}"

