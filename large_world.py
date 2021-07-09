import random
import sqlite3
from small_world import SmallWorld
from market_table import MarketTable
from agent_intelligence import dividendFirstOrderAdaptive
import database_manager as dm

class LargeWorld:
    # Attributes:
    # N: int                                    number of small worlds
    # S: int                                    number of states in L
    # E: float                                  endowment of each security in each small world
    # L: List[int]                              union of states in small worlds
    # small_worlds: dict{int:SmallWorld}        dictionary of key agent numbers and value SmallWorld objects
    # market_table: MarketTable                 our market making mechanism
    # use_backlog: bool                         if we should use a backlog
    # pick_agent_first: bool                    if True, we randomly pick an agent then a state in an iteration.
    #                                           if False, we randomly pick a state then an agent
    # con: Connection                           connection to database object
    # cur: Cursor                               Cursor object to execute database commands
    # beta: float                               beta for post-period first order adaptive process

    # Initialize large world based on the parameters in input file
    def __init__(self, p: dict):
        # Print all inputs received for debugging purposes
        print("Inputs:")
        for var_name, var in p.items():
            print(f"{var_name} : {var}")
        # Make sure our inputs are valid
        if p["fix_num_states"] and p["K"] > p["S"]:
            raise ValueError("Number of states in large world must be greater than number of states in small world")
        if not p["fix_num_states"] and p["K"] > p["N"]:
            raise ValueError("Number of small worlds must be greater than number of small worlds each state is in")

        # Initialize object variables
        self.S, self.E, self.beta = p["S"], p["E"], p["beta"]
        self.pick_agent_first = p["pick_agent_first"]
        self.use_backlog = p["use_backlog"]
        self.small_worlds = {}

        # If we fix the number of states, each world get K states
        if p["fix_num_states"]:
            self.N = p["N"]
            d = {}
            # Go through each agent and give them a random sample of size K securities
            # This agent is then added to the storage of small worlds
            for agent_num in range(self.N):
                agent = SmallWorld(agent_num, random.sample(range(self.S), p["K"]), self.E)
                for state_num in agent.states.keys():
                    if not d.get(state_num):
                        d[state_num] = True
                self.small_worlds[agent_num] = agent
            # All the states that are in the large world are put in L
            self.L = list(d.keys())
            self.L.sort()
        else:
            # states_list is an array with the states in each of the N agents
            self.L = range(self.S)
            states_list = []
            [states_list.append([]) for i in range(p["N"])]
            # Assign a random sample of K agents to each state
            for state_num in range(self.S):
                random_small_worlds = random.sample(range(p["N"]), p["K"])
                [states_list[i].append(state_num) for i in random_small_worlds]
            for agent_num in range(p["N"]):
                # There is a possibility that an agent gets assigned no states
                # In this case, it is excluded from the large world
                if states_list[agent_num]:
                    agent = SmallWorld(agent_num, states_list[agent_num], self.E)
                    self.small_worlds[agent_num] = agent
            self.N = len(self.small_worlds)

        # Set up database
        self.con = sqlite3.connect(p["file_name"] + ".db")
        self.cur = self.con.cursor()
        dm.createSimulationTables(self.cur)

        # Set up the dividend of agents
        i = 0
        for agent_num, agent in self.small_worlds.items():
            # If there are heterogenous dividend payoffs
            if p["is_custom"]:
                # Find the next num_trader type that needs an agent
                while p["num_traders_by_type"][i] == 0:
                    i+=1
                p["num_traders_by_type"][i] -= 1
            trader_type = i
            for state_num, state in agent.states.items():
                # Lookup the dividend we need from our dividends data structure
                # Otherwise, it is 1 by default
                dividend = p[trader_type][state_num] if p["is_custom"] else 1
                state.setDividend(dividend)
                # Store the dividend of each agent for each security in database
                self.cur.execute("INSERT INTO dividends VALUES (?, ?, ?, ?)", [agent_num, trader_type, state_num, dividend])

        # Set up market
        # Only include the states that are owned by some agents in marketplace
        self.market_table = MarketTable(self.L, self.small_worlds, p["by_midpoint"], self.cur, 
                                        p["alpha"], p["phi"], p["epsilon"], p["rep_flag"])

    # String representation of large world and the small worlds and state within it
    # Used for testing purposes
    def __str__(self) -> str:
        ans = f"This large world contains {self.N} agents with {len(self.L)} states\n"
        for small_world in self.small_worlds.values():
            ans += str(small_world)
        return ans

    # Initialize each agent's aspiration for their securities at the beginning of a period
    def giveMinimalIntelligence(self, period_num: int, R) -> None:
        # Iterate through each agent:
        for agent_num, small_world in self.small_worlds.items():
            states = list(small_world.states.keys())
            not_realized_states = list(filter(lambda s: s not in R, states))
            # Initialize not_info by randomly choosing half of the agent's states not included in R 
            not_info = random.sample(not_realized_states, len(not_realized_states) // 2)
            # Give this information to the current agent
            small_world.giveNotInfo(not_info)
            for state_num, state in small_world.states.items():
                # If the agent knows a state is not realized, its aspiration will be 0
                if state_num in not_info:
                    small_world.states[state_num].updateAspiration(0)
                    is_not_info, is_backlog = 1, 0
                # If the agent is unsure, it first checks the aspiration backlog. Otherwise, sets aspiration to dividend / C
                # If this simulation is using the backlog mechanism
                elif self.use_backlog:
                    is_not_info = 0
                    # Search the backlog
                    # If it returns -1, it means that the backlog search came back empty-handed
                    lookup = state.aspirationBacklogLookup()
                    if lookup == -1:
                        # If there is no backlog entry, aspiration is set to expected value assuming only state is realized
                        # ie. dividend payoff divided by the number of uncertain states
                        state.updateAspiration(state.dividend / state.parent_world.C)
                        is_backlog = 0
                    else:
                        state.updateAspiration(lookup)
                        is_backlog = 1
                # If the simulation is not using the backlog mechanism
                # In this case, the dividend payoff beta adjustment will have no effect
                else:
                    state.updateAspiration(state.dividend / state.parent_world.C)
                    is_backlog = 0
                is_not_info = 0
                self.cur.execute("INSERT INTO aspirations VALUES (?, ?, ?, ?, ?, ?, ?)",
                                [period_num, agent_num, state_num, small_world.C, state.aspiration, is_not_info, is_backlog])

    # Called at the beginning of a period
    # Resets the cash balance of each agent to 0
    # Re-endow each agent with E of each security they have
    def resetSmallWorlds(self) -> None:
        for small_world in self.small_worlds.values():
            small_world.balanceReset()
            for state in small_world.states.values():
                state.amountAdd(self.E)

    # Called at the end of a period to pay out all dividends as appropriate
    # Log how much of each security each agent has at the end of a period in security_balances table in database
    def realizePeriod(self, R, period_num: int) -> None:
        for small_world in self.small_worlds.values():
            for state_num, state in small_world.states.items():
                is_realized = 1 if state_num in R else 0
                self.cur.execute("INSERT INTO security_balances VALUES (?, ?, ?, ?, ?, ?, ?)",
                                [period_num, small_world.agent_num, state_num, state.amount, state.dividend, is_realized * state.amount * state.dividend, is_realized])
                # Pay out the dividends of a security and clear the security amounts
                # Update the aspiration backlog of each security if applicable
                if is_realized:
                    small_world.balanceAdd(state.amount * state.dividend)
                    if self.use_backlog:
                        state.updateAspirationBacklog(dividendFirstOrderAdaptive(state.aspiration, state.dividend, self.beta))
                # Security is not realized and backlog system must be updated
                elif self.use_backlog:
                    state.updateAspirationBacklog(dividendFirstOrderAdaptive(state.aspiration, 0, self.beta))
                state.amountReset()
    
    # Runs one period of the simulation
    def period(self, period_num: int, i: int, r: int) -> None:
        if r > self.S:
            raise ValueError("r must be <= number of states in large world")
        # We make the model choice that states not in any small worlds may still be realized
        # Initialize R by choosing r random states in the large world with equal probability to be realized 
        R = random.sample(range(self.S), r)
        # Store information about which states are unrealized and realized in this period in database
        dm.updateRealizationsTable(self.cur, period_num, self.S, R)
        # Clear all of the small worlds and give each agent information
        self.resetSmallWorlds()
        self.giveMinimalIntelligence(period_num, R)
        # Conduct each market making iteration using a single processor 
        for j in range(i):
            # Either pick a random agent and then a random state
            if self.pick_agent_first:
                rand_agent = random.choice(list(self.small_worlds.values()))
                rand_state = random.choice(list(rand_agent.states.values()))
            # Or a random state number and then a random agent's security of that same state number
            else:
                rand_state_num = random.choice(self.L)
                rand_state = random.choice(self.market_table.table[rand_state_num].reserve)

            # Randomly choose to either submit a bid or ask
            rand_action = random.choice(["bid", "ask"])
            if rand_action == "bid":
                bid = random.uniform(0, rand_state.aspiration)
                self.market_table.updateBidder(bid, rand_state, j)
            else:
                ask = random.uniform(rand_state.aspiration, rand_state.dividend)
                self.market_table.updateAsker(ask, rand_state, j)    
        # Finish the period
        self.market_table.tableReset()
        self.realizePeriod(R, period_num)
        dm.updateAgentsTable(self.cur, period_num, self.small_worlds.values())

    # Runs the simulation for the large world
    # Parameters
    # num_periods: int      number of periods to run the simulation for
    # i: int                number of market making iterations
    # r: int                number of states that will be realized, must be <= S
    def simulate(self, num_periods: int, i: int, r: int):
        # Run num_periods periods
        for period_num in range(num_periods):
            self.period(period_num, i, r)
            print(f"Finished running period {period_num}")
        # Save and close database connection
        self.con.commit()
        self.con.close()