# These functions serve as the mechanism through which our agents gain intelligence through market processes

# Anchor and adjust module
# Used to update aspiration for all agents with a given security after that security has been transacted
def priceFirstOrderAdaptive(aspiration: float, price: float, alpha: float) -> float:
    return alpha * price + (1 - alpha) * aspiration

# After a period is realized, all agents with that security calculate a new aspiration for this security based on its value
# This is then stored in the backlog for when the same value of C arises in the future
def dividendFirstOrderAdaptive(aspiration: float, dividend: int, beta: float) -> float:
    return beta * dividend + (1 - beta) * aspiration

# Representativeness module
# This price adjustment works complementary to post-transaction anchor and adjust
# If there has been a string of phi price transactions with decreasing/increasing prices, the we adjust aspiration to either 0 or epsilon
# This module is only called when such a price path is detected with is_decrease telling us whether it's an increasing or decreasing path
def detectPattern(phi: int, price_pattern: 'List[int]') -> str:
    if len(price_pattern) < phi or len(set(price_pattern[-1 * phi:])) != 1 or set(price_pattern[-1 * phi:]) == {0}:
        return None
    return "decreasing" if set(price_pattern[-1 * phi:]) == {-1} else "increasing"

def representativenessModule(epsilon: float, pattern: str) -> float:
    return epsilon if pattern == "decreasing" else 1