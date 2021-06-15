import sqlite3
import statistics as stat
import database_manager as dm
import plot_statistics as ps
import time

INT_INPUTS = ["N", "S", "E", "K", "num_periods", "i", "r"]
FLOAT_INPUTS = ["alpha", "beta"]
BOOL_INPUTS = ["fix_num_states", "by_midpoint", "pick_agent_first"]

# returns dictionary of parameters
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
    for i in INT_INPUTS:
        p[i] = int(p[i])
    for i in FLOAT_INPUTS:
        p[i] = float(p[i])
    for i in BOOL_INPUTS:
        p[i] = p[i] == "True"
    return p

# Calculate mean, standard deviation, and volumee of transactions of securities across different periods
# Store calculations in prices table in database
# Display quadrants of plots
def pricePathByPeriod(cur, p: dict) -> None:
    start = time.time()
    S = p["S"]
    dm.createPricesByPeriodTable(cur)
    num_periods = p["num_periods"]
    for state_num in range(S):
        price_data = []
        x = range(num_periods)
        for period_num in x:
            cur.execute("SELECT price FROM transactions WHERE state_num=? AND period_num=?", (state_num, period_num))
            rows = cur.fetchall()
            # No transactions during this period
            if not rows:
                price_data.append([])
                continue
            period_prices = list(map(lambda r: r[0], rows))
            price_data.append(period_prices)

        # Account for possibility that no agents have this security in their small world
        if not list(filter(lambda x: x, price_data)):
            continue

        # We log the mean as 0 if there are no transactions
        means = list(map(lambda z: stat.mean(z) if z else 0, price_data))
        # We log the standard deviation as 1 if there are not at least 2 data points
        sds = list(map(lambda z: stat.stdev(z) if len(z) > 1 else 0, price_data))
        volumes = list(map(len, price_data))
        cur.execute("SELECT realized FROM realizations WHERE state_num=?", (state_num,))
        # We make the assumption that the realized data is insered chronologically by period
        realized = list(map(lambda r: r[0], cur.fetchall()))

        # Update our database
        for i in range(num_periods):
            cur.execute("INSERT INTO prices_by_period VALUES (?, ?, ?, ?, ?, ?)", 
                        [state_num, i, means[i], sds[i], volumes[i], realized[i]])
    end = time.time()
    print(f"Sucessfully added price path by period statistics to database. This operation took {round(end-start, 1)} seconds to complete")

def pricePathByTransaction(cur, p: dict) -> None:
    start = time.time()
    # If we want to have all securities display up to the highest transaction, we just set max_transactions to the most number of transactions they have in a period
    S = p["S"]
    dm.createPricesByTransactionTable(cur)
    for state_num in range(S):
        cur.execute("SELECT MAX(transaction_num) FROM transactions WHERE state_num=?", (state_num,))
        max_transactions = cur.fetchone()[0]
        # Account for possibility that no agents have this security in their small world
        # We choose to ignore such states
        if not max_transactions:
            continue

        # Create a list with all the transactions that occur 
        price_data = []
        x = range(max_transactions)
        for t in x:
            cur.execute("SELECT price FROM transactions WHERE state_num=? AND transaction_num=?", (state_num, t))
            t_prices = list(map(lambda r: r[0], cur.fetchall()))
            price_data.append(t_prices)

        # We log the mean as 0 if there are no transactions
        means = list(map(lambda z: stat.mean(z) if z else 0, price_data))
        # We log the standard deviation as 1 if there are not at least 2 data points
        sds = list(map(lambda z: stat.stdev(z) if len(z) > 1 else 0, price_data))
        volumes = list(map(len, price_data))
        # Update db
        for t in x:
            cur.execute("INSERT INTO prices_by_transaction VALUES (?, ?, ?, ?, ?)",
                        [state_num, t, means[t], sds[t], volumes[t]])
    end = time.time()
    print(f"Sucessfully added price path by transaction statistics to database. This operation took {round(end-start, 1)} seconds to complete")

def plotsMenu(cur, p) -> None:
    print("Here are the plots you can view:")
    print("\t'1' for a plot of price path by period")
    print("\t'2' for a plot of price path by transaction number")
    print("\t'q' to quit viewing plots")
    i = input("Enter what plot(s) you want to see: ").strip().lower()
    if i == "q":
        return
    if i == "1":
        ps.plotPriceByPeriod(cur, p)
    elif i == "2":
        transaction_limit = input("How many transactions do you want to see at most for each security: ")
        try:
            ps.plotPriceByTransaction(cur, p, int(transaction_limit))
        except:
            pass
    else:
        print("Invalid input, try again!")
    plotsMenu(cur, p)

def runStatistics(db: str):
    con = sqlite3.connect(db)
    cur = con.cursor()
    p = obtainParameters(db[:-3] + ".in")

    # Create summary statistics in our database
    pricePathByPeriod(cur, p)
    pricePathByTransaction(cur, p)
    con.commit()

    # Display the plots that we want
    # plotsMenu(cur, p)
    con.close()