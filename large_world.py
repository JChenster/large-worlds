import random
import sqlite3
from small_world import SmallWorld
from market_table import MarketTable
from market_table2 import MarketTable2
from agent_intelligence import dividendFirstOrderAdaptive
import database_manager as dm

REPRESENTATIVENESS_MAX_PROBABILITY = .1

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
    # rep_threshold: int                        Either None if representativeness module is 1 or 2
    #                                           Or if it is module 3, its value is the iteration to start applying the representativeness heuristic
    # market_type: int                          The type of market

    # Variables used during the conduction of the simulation
    # period_num            Current period number
    # iteration_num         Current iteration number
    # R                     Realized states for the current period

    # Print all inputs received for debugging purposes
    def printInputs(self, p: dict):
        print("Inputs:")
        for var_name, var in p.items():
            print(f"{var_name} : {var}")

    def initializeDatabase(self, database_name: str) -> None:
        self.con = sqlite3.connect(database_name)
        self.cur = self.con.cursor()
        dm.createSimulationTables(self.cur)

    def initializeMarket(self, p: dict) -> None:
        # Set up market
        # Only include the states that are owned by some agents in marketplace
        if self.market_type == 1:
            self.market_table = MarketTable(self.L, self.small_worlds, p["by_midpoint"], self.cur, p["alpha"], p["phi"], p["epsilon"], p["rep_flag"])
        elif self.market_type == 2:
            self.market_table = MarketTable2(self.L, self.small_worlds, p["by_midpoint"], self.cur, p["alpha"])

    def initializeDividends(self, p: dict) -> None:
        # Set up the dividend of agents
        # i is a counter that represents the trader type of the current agent we are iterating through
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

    # Initialize large world based on the parameters in input file
    def __init__(self, p: dict):
        self.printInputs(p)

        # Error checking to make sure some of our inputs are valid
        if p["fix_num_states"] and p["K"] > p["S"]:
            raise ValueError("Number of states in large world must be greater than number of states in small world")
        if not p["fix_num_states"] and p["K"] > p["N"]:
            raise ValueError("Number of small worlds must be greater than number of small worlds each state is in")

        # Initialize object variables
        # These are all taken from the dictionary of parameters, self-explanatory
        self.S, self.E, self.beta = p["S"], p["E"], p["beta"]
        self.pick_agent_first = p["pick_agent_first"]
        self.use_backlog = p["use_backlog"]
        self.small_worlds = {}
        # rep_threhold could be None in which case it means the rep module is not 3
        self.rep_threshold = p.get("rep_threshold")
        self.market_type = p["market_type"]
        self.rho = p["rho"]

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
        # We instead fix the number of worlds that contain each state
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
                # We only create an agent object for those with at least 1 state
                if states_list[agent_num]:
                    agent = SmallWorld(agent_num, states_list[agent_num], self.E)
                    self.small_worlds[agent_num] = agent
            self.N = len(self.small_worlds)

        # Set up database
        self.initializeDatabase(p["file_name"] + ".db")
        self.initializeMarket(p)
        self.initializeDividends(p)   

    # String representation of large world and the small worlds and state within it
    # Used for testing purposes
    def __str__(self) -> str:
        ans = f"This large world contains {self.N} agents with {len(self.L)} states\n"
        for small_world in self.small_worlds.values():
            ans += str(small_world)
        return ans

    # Based on the states that are realized, give partial information to a trader 
    # Out of the unrealized states, tell them roughly half of them
    def informTrader(self, trader: 'SmallWorld') -> None:
        states = list(trader.states.keys())
        not_realized_states = list(filter(lambda s: s not in self.R, states))
        # Initialize not_info by randomly choosing half of the agent's states not included in R
        not_info = random.sample(not_realized_states, len(not_realized_states) // 2)
        # Give this information to the current agent
        trader.giveNotInfo(not_info)

    # Initialize the aspiration of a security for a trader based on the information it has received
    # for that period
    def initializeAspiration(self, trader: 'SmallWorld', state: 'State') -> None:
        # If the agent knows a state is not realized, its aspiration will be 0
        if state.getStateNum() in trader.getNotInfo():
            trader.getStatesMap()[state.getStateNum()].updateAspiration(0)
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
                state.updateAspiration(state.getDividend() / trader.getC())
                is_backlog = 0
            else:
                state.updateAspiration(lookup)
                is_backlog = 1
        # If the simulation is not using the backlog mechanism
        # In this case, the dividend payoff beta adjustment will have no effect
        else:
            state.updateAspiration(state.dividend / trader.getC())
            is_backlog = 0
        is_not_info = 0
        # Store initial aspirations levels in aspirations table of our databae
        self.cur.execute("INSERT INTO aspirations VALUES (?, ?, ?, ?, ?, ?, ?)",
                        [
                            self.period_num, 
                            trader.getAgentNum(), 
                            state.getStateNum(), 
                            trader.getC(),
                            state.getAspiration(),
                            is_not_info,
                            is_backlog
                        ]
        )

    # Initialize each agent's aspiration for their securities at the beginning of a period
    def giveMinimalIntelligence(self) -> None:
        # Iterate through each agent:
        for small_world in self.small_worlds.values():
            # Give partial information to an agent
            self.informTrader(small_world)
            for state in small_world.getStateObjects():
                # Initialize aspiration for our security for this security
                self.initializeAspiration(small_world, state)

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
    def realizePeriod(self) -> None:
        for small_world in self.small_worlds.values():
            for state_num, state in small_world.getStatesMap().items():
                is_realized = 1 if state_num in self.R else 0
                self.cur.execute("INSERT INTO security_balances VALUES (?, ?, ?, ?, ?, ?, ?)",
                                [
                                    self.period_num, 
                                    small_world.agent_num, 
                                    state_num, 
                                    state.amount, 
                                    state.getDividend(), 
                                    is_realized * state.getAmount() * state.getDividend(), 
                                    is_realized
                                ]
                )
                # Pay out the dividends of a security and clear the security amounts
                # Update the aspiration backlog of each security if applicable
                # Security was realized
                if is_realized:
                    small_world.balanceAdd(state.amount * state.dividend)
                    if self.use_backlog:
                        state.updateAspirationBacklog(dividendFirstOrderAdaptive(state.aspiration, state.dividend, self.beta))
                # Security was not realized
                elif self.use_backlog:
                    state.updateAspirationBacklog(dividendFirstOrderAdaptive(state.aspiration, 0, self.beta))
                state.amountReset()

    # Picks a random security to submit a bid/ask for
    # Used in market type 1
    def pickRandomState(self):
        # Either pick a random agent and then a random state
        if self.pick_agent_first:
            rand_agent = random.choice(self.getAgents())
            return random.choice(list(rand_agent.getStateObjects()))
        # Or a random state number and then a random agent's security of that same state number
        else:
            rand_state_num = random.choice(self.L)
            return random.choice(self.market_table.getMarket(rand_state_num).getReserve())

    def repModule3(self) -> None: 
        # First randomly generate a probability threshold that applies to all agents
        p = random.uniform(0, REPRESENTATIVENESS_MAX_PROBABILITY)
        # Generate a random number for each agent
        # If their random number is below the probability threshold, enact rep module 3
        # For each agent that rep module 3 applies to, it searches among its securities
        # And identifies the one with the closest dividend to the latest transaction price in the market
        # And then, it sets the aspiration of that security to its personal dividend
        # And everything else to 0
        for agent in self.getAgents():
            # Make sure that there is a previous transaction to base judgement on
            latest_price = self.market_table.getLatestPrice()
            if random.uniform(0, 1) < p and latest_price != -1:
                closest_dividend = agent.getClosestDividend(latest_price)
                for state_num, dividend in agent.getUncertainStatesMap().items():
                    # This implicitly assumes agents will not have the same dividend for different securities
                    # ie. representativeness heuristic 3 only works with heterogenous dividend preferences across securities
                    # Assumption is CAL is set to state dividend if a security has the closest dividend payoff to the latest transaction
                    if dividend == closest_dividend:
                        agent.getSecurity(state_num).updateAspiration(dividend)
                        # if period_num < 3: print(f"Period num: {period_num}, iteration num: {iteration_num}, deduced for agent {agent.agent_num}, security {state_num} must be realized")
                    # All other securities are presumed to be unrealized ie. CAL is 0
                    else:
                        agent.getSecurity(state_num).updateAspiration(0)

    # Conducts an iteration for a market of type 1
    def marketType1Iteration(self) -> None:
        rand_state = self.pickRandomState()
        # At this point, rand_state is a security that we want to submit a bid/ask for for a certain agent
        # Randomly choose to either submit a bid or ask
        rand_action = random.choice(["bid", "ask"])
        # If a bid is chosen, then a bid is generated between 0 and the state's CAL for that security
        if rand_action == "bid":
            bid = random.uniform(0, rand_state.aspiration)
            self.market_table.updateBidder(bid, rand_state, self.iteration_num)
        # Or an ask is generated between the agent's CAL and what they know to be the payoff that security
        else:
            ask = random.uniform(rand_state.aspiration, rand_state.dividend)
            self.market_table.updateAsker(ask, rand_state, self.iteration_num)

        # If self.rep_threshold is not None, then trigger representativeness module 3
        if self.rep_threshold is not None and self.rep_threshold < self.iteration_num:
            self.repModule3()

    # Implements the representativeness module used in Mike's implementation of Rational Expectations
    # First, to add a little bit of irrationality, 1 agent is randomly chosen to have the representativeness module apply to them
    # If it does, then using the information they know, they fill find the security that has the highest minimum price
    # That has not been ruled out yet and sets the aspiration for that to the dividend payout and the others to 0
    # This means that the market must keep track of the minimum price for a given period
    def repModuleMike(self):
        random_agent = random.choice(self.getAgents())
        # We want to find the smallest minimum prices across all securities that are unknown
        minMinPrice = 1
        for state_num, state in random_agent.states.items():
            if state_num not in random_agent.not_info:
                minPrice = self.market_table.getMarketMinPrice(state_num)
                if minPrice < minMinPrice:
                    minMinPrice = minPrice

        for state_num, state in random_agent.states.items():
            if (
                state_num not in random_agent.not_info
                and self.market_table.getMarketMinPrice(state_num) == minMinPrice
            ):
                state.updateAspiration(0)
                # print(f"Rep Module, iteration {iteration_num}, security {state_num} CAL set to {state.dividend}")
            else:
                state.updateAspiration(state.dividend)

    # Next, in each iteration, each agent generates a random price for each of its securities
    # Based on this price, the action is classified as a bid or ask in a fashion that may not be 50/50 as it is in market type 1
    # Only after this occures for each agent is a market clearing transaction conducted
    def genBidAsk(self):
        for agent in self.getAgents():
            for state in agent.getStatesMap().values():
                random_price = random.uniform(0, 1)
                # Ask
                if random_price > state.getAspiration():
                    self.market_table.updateAsker(random_price, state, self.iteration_num)
                # Bid
                else:
                    self.market_table.updateBidder(random_price, state, self.iteration_num)

    # Conducts an iteration for a market of type 2
    # In market type 2, the double auction is not quite continuous
    # Instead transactions are only conducted after each agent has had the chance to bid/ask on each of its securities
    def marketType2Iteration(self) -> None:
        rand_num = random.uniform(0, 1)
        rand_rho = random.uniform(0, 1) * self.rho
        # We only apply representativeness module if representativeness module 3 is indicated
        # And the random condition is fulfilled
        if (
            self.rep_threshold is not None
            and self.iteration_num > self.rep_threshold 
            and rand_num > rand_rho
        ):
            self.repModuleMike()
        self.genBidAsk()
        self.market_table.tableMarketMake(self.iteration_num)
    
    # Runs one period of the simulation
    def period(self, i: int, r: int) -> None:
        if r > self.S:
            raise ValueError("r must be <= number of states in large world")
        # We make the model choice that states not in any small worlds may still be realized
        # Self.S contains simply a list of the number of states, which includes states that are possibly outside the scope of any agent
        # Initialize R by choosing r random states in the large world with equal probability to be realized 
        self.R = random.sample(range(self.S), r)
        # Store information about which states are unrealized and realized in this period in database
        dm.updateRealizationsTable(self.cur, self.period_num, self.S, self.R)
        # Reset the balance and endowment of each of our agents
        self.resetSmallWorlds()
        # Give information to each of our agent
        self.giveMinimalIntelligence()
        # Conduct each market making iteration using a single processor 
        for iteration_num in range(i):
            self.iteration_num = iteration_num
            # Conduct the appropriate iteration depending on what type of market it is
            if self.market_type == 1:
                self.marketType1Iteration()
            elif self.market_type == 2:
                self.marketType2Iteration()
        # Finish the period
        self.market_table.tableReset()
        self.realizePeriod()
        dm.updateAgentsTable(self.cur, self.period_num, self.small_worlds.values())

    # Runs the simulation for the large world
    # Parameters
    # num_periods: int      number of periods to run the simulation for
    # i: int                number of market making iterations
    # r: int                number of states that will be realized, must be <= S
    def simulate(self, num_periods: int, i: int, r: int):
        # Run num_periods periods
        for period_num in range(num_periods):
            self.period_num = period_num
            self.period(i, r)
            print(f"Finished running period {period_num}")
        # Save and close database connection
        self.con.commit()
        self.con.close()

    def getAgents(self) -> 'List[SmallWorld]':
        return list(self.small_worlds.values())

    def getAgent(self, agent_num) -> SmallWorld:
        return self.small_worlds[agent_num]