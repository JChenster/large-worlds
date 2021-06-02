class State:
    # Attributes:
    # state_num: int            the number of the state in large world
    # amount: int               the amount of state that small world has
    # aspiration: float         the aspiration level that small world assigns to this state
    # parent_world: SmallWorld  reference to small world that contains this state

    # Initialize a state with its state number and its endowment amount
    def __init__(self, parent_world, state_num: int, endowment: float):
        self.state_num = state_num
        self.amount = endowment
        self.aspiration = 0
        self.parent_world = parent_world

    def updateAspiration(self, aspiration: float) -> None:
        self.aspiration = aspiration
    
    def amountAdd(self, amount: int) -> None:
        self.amount += amount

    def __str__(self):
        return f"{self.amount} of state {self.state_num}, aspiration: {round(self.aspiration,2)}"