# These functions serve as the mechanism through which our agents gain intelligence through market processes

def priceFirstOrderAdaptive(aspiration: float, price: float, alpha: float) -> float:
    return alpha * price + (1 - alpha) * aspiration

def dividendFirstOrderAdaptive(aspiration: float, dividend: int, beta: float) -> float:
    return beta * dividend + (1 - beta) * aspiration