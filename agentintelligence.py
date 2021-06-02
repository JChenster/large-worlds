# alpha is a parameter that we can modify, set at .05 by default
def aspirationFirstOrderAdaptive(aspiration: float, price: float, alpha = .05) -> float:
    return alpha * price + (1 - alpha) * aspiration