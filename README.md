# Large Worlds

## Top Level Description
Computational economics research project conducted at the Yale School of Management under the guidance of Professor Sunder

## Project Description
We collectively live in a large world, but individually we exist in a small world where we are only aware of a subset of the large world. In tradtional economic theory, we make decisions by accessing the statistical probability of certain events occuring similarly to how we can calculate the expected value of a dice roll. What happens, however, if we are uncertain about everything that exists outside of our small world in the large world, and the probability of each event occuring is ambiguous? The objective of this simulation project is to gain insights on whether artificially intelligent agents operating in separate small worlds are able to aggregate information and succeed by participating in a double auction market and gaining insights from it.

## Running the Project
```
python3 main.py
```

## Project Components

* `large_world.py` Implements concept of a large world which in turn is composed of small worlds

  * `small_world.py` Implements our concept of small worlds which contains multiple states

    * `state.py` Implements our concept of an Arrow-Debreu security owned by an agent

  * `agent_intelligence.py` Mechanism to configure the intelligence of our agents

* `market_table.py`, `market.py` Implements a double auction market which we utilize to enable agents to trade

* `main.py` Receives input from user and conducts the necessary actions

  * `database_manager.py` Functions to store results of our simulation in an SQL database

  * `simulation_statistics.py` Calculates summary statistics on our simulation and stores them in database

* `plot_statistics.Rmd` Plots information of interest using R
