# These functions serve as the mechanism through which our agents gain intelligence through market processes

# Used to update aspiration for all agents with a given security after that security has been transacted
def priceFirstOrderAdaptive(aspiration: float, price: float, alpha: float) -> float:
    return alpha * price + (1 - alpha) * aspiration

# After a period is realized, all agents with that security calculate a new aspiration for this security based on its value
# This is then stored in the backlog for when the same value of C arises in the future
def dividendFirstOrderAdaptive(aspiration: float, dividend: int, beta: float) -> float:
    return beta * dividend + (1 - beta) * aspiration