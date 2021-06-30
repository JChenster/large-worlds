class State:
    # Attributes:
    # state_num: int                            the number of the state in large world
    # amount: int                               the amount of state that small world has
    # aspiration: float                         the aspiration level that small world assigns to this state
    # parent_world: SmallWorld                  reference to small world that contains this state
    # aspiration_backlog: dict{tuple: float}    dictionary linking not_info with dividend first order adaptive
    # dividend: float                           payoff of dividend

    # Initialize a state with its state number and its endowment amount
    def __init__(self, parent_world, state_num: int, endowment: float):
        self.state_num = state_num
        self.amount = endowment
        self.aspiration = 0
        self.parent_world = parent_world
        self.aspiration_backlog = dict()

    def updateAspiration(self, aspiration: float) -> None:
        self.aspiration = aspiration

    # The aspiration backlog holds the aspiration of the last time the agent received the same pieces of information
    # The number of combinations substantially increases with the number of pieces of information an agent gets in a period
    def updateAspirationBacklog(self, aspiration: float) -> None:
        self.aspiration_backlog[tuple(self.parent_world.not_info)] = aspiration

    # Returns backlogged dividend first order adapative aspiration if agent has previously obtained this value of C bebfore
    # Otherwise, return -1
    def aspirationBacklogLookup(self) -> float:
        lookup = self.aspiration_backlog.get(tuple(self.parent_world.not_info))
        return lookup if lookup is not None else -1
    
    def amountAdd(self, amount: int) -> None:
        self.amount += amount

    def amountReset(self) -> None:
        self.amount = 0

    def setDividend(self, dividend: float) -> None:
        self.dividend = dividend

    def __str__(self):
        return f"{self.amount} of state {self.state_num}, aspiration: {round(self.aspiration,2)}"