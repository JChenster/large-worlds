class State:
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

