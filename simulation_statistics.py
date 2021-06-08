import matplotlib.pyplot as plt
import sqlite3
import statistics as stat
from matplotlib.backends.backend_pdf import PdfPages

PRICE_COLUMN = 6

# returns dictionary of parameteres
def obtainParameters(input_file):
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

# Calculate mean and standard deviation of prices of securities across different periods
def pricePath(cur, p) -> None:
    # We build a dictionary of key securities
    # Values: List[List[int]] where inner list is transaction prices in a period
    # price_dict[A][B] represents the prices for security A in period B
    price_dict = dict()
    for state_num in range(p["S"]):
        price_dict[state_num] = []
        for period_num in range(p["num_periods"]):
            period_prices = []
            cur.execute("SELECT * FROM transactions WHERE state_num=? AND period_num=?", (state_num, period_num))
            rows = cur.fetchall()
            for row in rows:
                period_prices.append(row[PRICE_COLUMN])
            price_dict[state_num].append(period_prices)
    
    for state_num in range(p["S"]):
        price_data = price_dict[state_num]
        # We log the mean as 0 if there are no transactions
        means = list(map(lambda z: stat.mean(z) if z else 0, price_dict[state_num]))
        # We log the standard deviation as 1 if there are not at least 2 data points
        sds = list(map(lambda z: stat.stdev(z) if len(z) > 1 else 0, price_dict[state_num]))
        
        plt.plot(means)
        plt.title(f"Transaction prices of security {state_num}")
        plt.xlabel("Period")
        plt.ylabel("Price")
        plt.xticks(range(len(means)))
        plt.yticks([y/10 for y in range(11)])
        plt.show()

def runStatistics(db: str):
    con = sqlite3.connect(db)
    cur = con.cursor()
    p = obtainParameters(db[:-3] + ".in")
    pricePath(cur, p)