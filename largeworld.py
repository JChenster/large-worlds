import random
from smallworld import SmallWorld

class LargeWorld:
    # Attributes:
    # N: int (number of small worlds)
    # S: int (number of states)
    # small_worlds: List[SmallWorld] (list of SmallWorld objects) 

    # Parameters include N agents, S states, E endowment of each state for each agent, and K which can have one of 2 meanings
    # fixNumStates is configured as True by default in which each small world gets K states
    # fixNumWorlds can also be configured as True in which each state is assigned to K worlds
    def __init__(self, N: int, S: int, E: int, K: int, fixNumStates = True, fixNumWorlds = False):
        # Make sure our inputs are valid
        if fixNumStates and fixNumWorlds or not(fixNumStates or fixNumWorlds):
            raise ValueError("Exactly one of fixNumStates or fixNumWorlds must be configured")
        if fixNumStates and K > S:
            raise ValueError("Number of states in large world must be greater than number of states in small world")
        if fixNumWorlds and K > N:
            raise ValueError("Number of small worlds must be greater than number of small worlds each state is in")
        
        self.N = N
        self.S = S
        self.small_worlds = []

        # Each world get K states
        if fixNumStates:
            for agent_num in range(N):
                agent = SmallWorld(agent_num, random.sample(range(S), K), E)
                self.small_worlds.append(agent) 
        # Each state is placed in K worlds
        else:
            # states_list represents an array with the states in each of the N agents
            states_list = []
            [states_list.append([]) for i in range(N)]
            for state in range(S):
                random_small_worlds = random.sample(range(N), K)
                [states_list[i].append(state) for i in random_small_worlds]
            for agent_num in range(N):
                agent = SmallWorld(agent_num, states_list[agent_num], E)
                self.small_worlds.append(agent)

    def __str__(self):
        ans = f"This large world contains {self.N} agents with {self.S} states\n"
        for small_world in self.small_worlds:
            ans += str(small_world)
        return ans
    
    def event(self, r = 1):
        # Initialize R by choosing r random states from L with equal probability to be realized 
        R = random.sample(range(self.S), r)
        # Iterate through each agent:
        for small_world in self.small_worlds:
            states = list(small_world.states.keys())
            not_realized_states = list(filter(lambda s: s not in R, states))
            # Initialize not_info by randomly choosing half of the agent's states not included in R 
            not_info = random.sample(not_realized_states, len(not_realized_states) // 2)
            
            # Agent updates aspiration level of states in not_info to 0
            for state in not_info:
                small_world.states[state].updateAspiration(0)
            # Set aspiration levels for states with unknown payoff
            C = small_world.num_states - len(not_info)
            for state in states:
                if state not in not_info:
                    small_world.states[state].updateAspiration(1/C)
