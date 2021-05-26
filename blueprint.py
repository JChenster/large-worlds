# Create a class LargeWorld representing the large world
#   Attributes: array of SmallWorld, N, S
#
#   Constructor takes parameters S states, N agents
#       LargeWorld creates N instances of SmallWorld and creates them in one of the two ways using parameter K
#           A) Fixing number of states in each agent
#           B) Fix number of worlds for each S state to be included in
#
#   event(r: int) function simulates what happens in each period
#       Initialize R by choosing r random states from L with equal probability to be realized
#       Iterate through each agent:
#           Initialize not_info by randomly choosing half of the agent's states not included in R
#           Agent updates aspiration level of states in not_info to 0
#           C = number of states in small world - len(not_info)
#           Set aspiration level A of states not in not_info to 1/C
#       Undergo simulation iteraions (requires parameter I):
#           Randomly pick one of the N agents, one of its states, and bid or ask
#           Use hash tables to store bids and asks for each state, which will in turn be stored in max and min heaps respectively
#               Stored as [SmallWorld, bid/ask price]
#           marketMakerBid(agent: SmallWorld, bid: float) -> float: will update the bid hash table and see if the min ask works
#           marketMakerAsk(agent: SmallWorld, ask: float) -> float:  will update the ask hash table and see if the max bid works
#           After a successful transaction, price is returned, bid/ask hash table is updated, state amounts and SmallWorld balances are adjusted
#           Update agent aspirations as necessary
#               An advanced addition would be to incorporate trading in unimagined states
#       Realize the event and adjust cash balances as necessary
#           An advanced feature would be different preferences
#
#   Multiple rounds:
#       A) To keep the small worlds unchanged, simply call event() again. Need to handle issue of liquidated securities
#       B) Add some/all of the realized events to small worlds presumably with 0 endowment and run event() again
#
#   To start with a new large world, make a new instance of LargeWorld

# SmallWorld is a subclass of LargeWorld that represents a small world in a large world
#   Attributes: balance, array of State, not_info
#   Constructor: initialize states that are present in the small world and endow them with E of each state

# State is a subclass of SmallWorld containing necessary information for states in a small world
#   Attributes: amount, bid, ask, aspiration
#   Can be updated with function updateAspiration(state: int, aspiration: float)
#   This function is used to update aspiration after a transaction
#       firstOrderAdapative(aspiration: float, price: float) -> float;
#   Other functions for other adjustment processes can also be written to add more agent intelligence

