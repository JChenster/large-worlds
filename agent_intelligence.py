# These functions serve as the mechanism through which our agents gain intelligence through market processes

# alpha is a parameter that we can modify, set at .05 by default
def priceFirstOrderAdaptive(aspiration: float, price: float, alpha = .05) -> float:
    return alpha * price + (1 - alpha) * aspiration

# beta is a parameter that we can modify, set at .25 by default
def dividendFirstOrderAdaptive(aspiration: float, dividend: int, beta = .25) -> float:
    return beta * dividend + (1 - beta) * aspiration