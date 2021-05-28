class State:
    # Attributes:
    # state_num: int (the number of the state in large world)
    # amount: int (the amount of state that small world has)
    # aspiration: float (the aspiration level that small world assigns to this state)
    # bid: float (the small world's current bid for this state)
    # ask: float (the small world's current ask for this state)

    # Initialize a state with its state number and its endowment amount
    def __init__(self, state_num, endowment: float):
        self.state_num = state_num
        self.amount = endowment
        self.aspiration = self.bid = self.ask = 0

    def updateAspiration(self, aspiration: float) -> None:
        self.aspiration = aspiration

    def firstOrderAdaptive(self, aspiration: float, price: float) -> float:
        pass

    def __str__(self):
        return f"{self.amount} of state {self.state_num}"

