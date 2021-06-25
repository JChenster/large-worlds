# Large Worlds

## Top Level Description
Computational economics research project conducted at the Yale School of Management under the guidance of Professor Sunder

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
