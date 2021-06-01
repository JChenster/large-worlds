# alpha is a parameter that we can modify, set at .5 by default
def aspirationFirstOrderAdaptive(aspiration: float, price: float, alpha = .5) -> float:
    return alpha * price + (1 - alpha) * aspiration