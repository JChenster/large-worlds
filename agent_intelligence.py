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
# The representativeness adjustment works complementary to post-transaction anchor and adjust
# If there has been a string of phi price transactions with decreasing/increasing prices, the we adjust aspiration to either 0 or epsilon
# There is a special case in which if a decreasing pattern is detected but epsilon is greater than our current aspiration, we don't do anything
def detectPattern(phi: int, price_pattern: 'List[int]') -> str:
    # print(f"price pattern: {price_pattern[-1*phi:]}")
    if len(price_pattern) < phi or len(set(price_pattern[-1 * phi:])) != 1 or set(price_pattern[-1 * phi:]) == {0}:
        return None
    return "decreasing" if set(price_pattern[-1 * phi:]) == {-1} else "increasing"

# There are 2 instances of the representativeness adjustment module
# This adjustment is only used when such a price path is detected
def representativenessAdjustment1(state: 'State', epsilon: float, pattern: str) -> float:
    # No pattern
    if pattern is None:
        return state.aspiration
    # There is a decreasing pattern but epsilon is above current aspiration
    if pattern == "decreasing" and epsilon > state.aspiration:
        return state.aspiration
    return epsilon if pattern == "decreasing" else state.dividend

def representativenessAdjustment2(state: 'State', epsilon: float, pattern: str) -> float:
    # Only enact change if there is a decreasing pattern
    if pattern != "decreasing":
        return state.aspiration
    # Only multiply other securities by the approriate factor when we have not already ruled out this state
    if state.state_num in state.parent_world.getUncertainStates():
        # print(f"Noticed decreasing pattern for {state.state_num}")
        state.parent_world.C -= 1
        state.parent_world.removeUncertain(state.state_num)
        if state.parent_world.C != 0:
            for other_state in state.parent_world.states.values():
                # Only enact multiplier for states that are uncertain
                if other_state is not state and other_state.state_num in state.parent_world.uncertain:
                    # Shouldn't increase the aspiration level beyond the payoff of the security
                    other_state.updateAspiration(min(state.aspiration * (state.parent_world.C + 1) / state.parent_world.C, state.dividend))
                    # print(f"Changed security: {other_state.state_num} to aspiration: {other_state.aspiration}")
    return epsilon if epsilon < state.aspiration else state.aspiration