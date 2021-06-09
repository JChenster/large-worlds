import matplotlib.pyplot as plt
import sqlite3
import statistics as stat
import database_manager as dm

PRICE_COLUMN = 6
PLOT_ROWS, PLOT_COLS = 2, 2

# returns dictionary of parameteres
def obtainParameters(input_file: str) -> dict:
    f = open(input_file, "r")
    p = dict()
    while True:
        line = f.readline()
        if not line:
            break
        p[line.split(":")[0]] = line.split(":")[1].strip()
    f.close()
    
    # Clean up our int/bool inputs
    int_inputs = ["N", "S", "E", "K", "num_periods", "i", "r"]
    for i in int_inputs:
        p[i] = int(p[i])
    bool_inputs = ["fix_num_states", "by_midpoint"]
    for i in bool_inputs:
        p[i] = bool(p[i])
    return p

# Calculate mean, standard deviation, and volumee of transactions of securities across different periods
# Store calculations in prices table in database
# Display quadrants of plots
def pricePathByPeriod(cur, p: dict, display_plots = True) -> None:
    # We build a dictionary of key securities
    # Values: List[List[int]] where inner list is transaction prices in a period
    # price_dict[A][B] represents the prices for security A in period B
    price_dict = dict()
    S = p["S"]
    for state_num in range(S):
        price_dict[state_num] = []
        for period_num in range(p["num_periods"]):
            period_prices = []
            cur.execute("SELECT * FROM transactions WHERE state_num=? AND period_num=?", (state_num, period_num))
            rows = cur.fetchall()
            for row in rows:
                period_prices.append(row[PRICE_COLUMN])
            price_dict[state_num].append(period_prices)

    dm.createPricesByPeriodTable(cur)
    num_periods = p["num_periods"]
    offset = 0
    for state_num in range(S):
        price_data = price_dict[state_num]
        # We log the mean as 0 if there are no transactions
        means = list(map(lambda z: stat.mean(z) if z else 0, price_data))
        # We log the standard deviation as 1 if there are not at least 2 data points
        sds = list(map(lambda z: stat.stdev(z) if len(z) > 1 else 0, price_data))
        volumes = list(map(len, price_data))
        x = range(num_periods)

        cur.execute("SELECT realized FROM realizations WHERE state_num=?", (state_num,))
        realized = list(map(lambda x: x[0], cur.fetchall()))

        # Update our database
        for i in range(num_periods):
            cur.execute("INSERT INTO prices_by_period VALUES (?, ?, ?, ?, ?, ?)", 
                        [state_num, i, means[i], sds[i], volumes[i], realized[i]])

        if display_plots:
            if state_num == offset:
                fig, axs = plt.subplots(PLOT_ROWS, PLOT_COLS)

            pos = state_num - offset
            axs[pos // PLOT_ROWS, pos % PLOT_COLS].plot(means)
            axs[pos // PLOT_ROWS, pos % PLOT_COLS].set(
                title = f"Transaction prices of security {state_num}",
                xlabel = "Period",
                ylabel = "Price",
                xticks = x,
                yticks = [y/10 for y in range(11)]
            )
            means_label = map(lambda m: round(m, 3), means)
            sds_label = map(lambda s: round(s, 2), sds)
            # We annotate from top to bottom: mean, standard deviation, volume, whether realized
            for z in zip(x, means_label, sds_label, volumes, realized):
                axs[pos // PLOT_ROWS, pos % PLOT_COLS].annotate(f"{z[1]}", xy = (z[0], z[1] + .3))
                axs[pos // PLOT_ROWS, pos % PLOT_COLS].annotate(f"{z[2]}", xy = (z[0], z[1] + .2))
                axs[pos // PLOT_ROWS, pos % PLOT_COLS].annotate(f"{z[3]}", xy = (z[0], z[1] + .1))
                axs[pos // PLOT_ROWS, pos % PLOT_COLS].annotate(f"{'R' if z[4] else 'N'}", xy = (z[0], z[1]))

            # It's time to show a new batch of plots or this is the last plot
            if state_num == offset + PLOT_ROWS * PLOT_COLS - 1 or state_num == S - 1:
                plt.tight_layout()
                plt.show()
                plt.close()
                offset += PLOT_ROWS * PLOT_COLS

    print(f"Sucessfully added price path statistics to database")
    if display_plots:
        print(f"Successfully generated price path plots")

def pricePathByTransaction(cur, p: dict, max_transactions: int, display_plots = True):
    # If we want to have all securities display up to the highest transaction, we just set max_transaction to the most number of transactions they have in a period
    S = p["S"]
    dm.createPricesByTransactionTable(cur)
    for state_num in range(S):
        # Create a list with all the transactions that occur 
        price_data = []
        x = range(max_transactions)
        for t in x:
            t_prices = []
            cur.execute("SELECT price FROM transactions WHERE state_num=? AND transaction_num=?", (state_num, t))
            rows = cur.fetchall()
            [t_prices.append(row[0]) for row in rows]
            price_data.append(t_prices)

        # We log the mean as 0 if there are no transactions
        means = list(map(lambda z: stat.mean(z) if z else 0, price_data))
        # We log the standard deviation as 1 if there are not at least 2 data points
        sds = list(map(lambda z: stat.stdev(z) if len(z) > 1 else 0, price_data))
        volumes = list(map(len, price_data))
        x = range(max_transactions)
        # Update db
        for t in x:
            cur.execute("INSERT INTO prices_by_transaction VALUES (?, ?, ?, ?, ?)",
                        [state_num, t, means[t], sds[t], volumes[t]])
        if display_plots:
            plt.plot(means)
            plt.title(f"Transaction prices of security {state_num}")
            plt.xlabel("Transaction number")
            plt.ylabel("Price")
            plt.xticks(x)
            plt.yticks([y/10 for y in range(11)])

            means_label = map(lambda m: round(m, 3), means)
            sds_label = map(lambda s: round(s, 2), sds)
            # We annotate from top to bottom: mean, standard deviation, volume
            for z in zip(x, means_label, sds_label, volumes):
                plt.annotate(f"{z[1]}", xy = (z[0], z[1] + .2))
                plt.annotate(f"{z[2]}", xy = (z[0], z[1] + .1))
                plt.annotate(f"{z[3]}", xy = (z[0], z[1]))
            plt.show()
            plt.clf()

def runStatistics(db: str):
    con = sqlite3.connect(db)
    cur = con.cursor()
    p = obtainParameters(db[:-3] + ".in")
    pricePathByPeriod(cur, p, display_plots = False)
    pricePathByTransaction(cur, p, 15, display_plots = True)
    # Save and close database connection
    con.commit()
    con.close()