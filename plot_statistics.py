import matplotlib.pyplot as plt

# Constants that can be modified as necessary
# The index number of various columns in our database
PRICEBYPERIOD_MEAN_COL = 2
PRICEBYPERIOD_STDEV_COL = 3
PRICEBYPERIOD_VOLUME_COL = 4
PRICEBYPERIOD_REALIZED_COL = 5

PRICEBYTRANSACTION_MEAN_COL = 2
PRICEBYTRANSACTION_STDEV_COL = 3
PRICEBYTRANSACTION_VOLUME_COL = 4

# How many rows and columns we want our plots of price path by period to have
PLOT_ROWS, PLOT_COLS = 2, 2

# How we should display our data
MEANS_ROUND = 3
STDEV_ROUND = 3
PRICEBYPERIOD_LABEL_OFFSET = .1
PRICEBYTRANSACTION_LABEL_OFFSET = .05

def plotPriceByPeriod(cur, p: dict) -> None:
    S = p["S"]
    offset = 0
    x = range(p["num_periods"])
    for state_num in range(S):
        if state_num == offset:
            fig, axs = plt.subplots(PLOT_ROWS, PLOT_COLS)

        cur.execute("SELECT * from prices_by_period WHERE state_num=?", (state_num,))
        rows = cur.fetchall()
        means = list(map(lambda r: r[PRICEBYPERIOD_MEAN_COL], rows))
        sds = list(map(lambda r: r[PRICEBYPERIOD_STDEV_COL], rows))
        volumes = list(map(lambda r: r[PRICEBYPERIOD_VOLUME_COL], rows))
        realizeds = list(map(lambda r: r[PRICEBYPERIOD_REALIZED_COL], rows))

        pos = state_num - offset
        axs[pos // PLOT_ROWS, pos % PLOT_COLS].plot(means)
        axs[pos // PLOT_ROWS, pos % PLOT_COLS].set(
            title = f"Transaction prices of security {state_num}",
            xlabel = "Period",
            ylabel = "Price",
            xticks = x,
            yticks = [y/10 for y in range(11)]
        )
        means_label = map(lambda m: round(m, MEANS_ROUND), means)
        sds_label = map(lambda s: round(s, STDEV_ROUND), sds)
        # We annotate from top to bottom: mean, standard deviation, volume, whether realized
        for z in zip(x, means_label, sds_label, volumes, realizeds):
            for j in range(1, 4):
                axs[pos // PLOT_ROWS, pos % PLOT_COLS].annotate(f"{z[j]}", xy = (z[0], z[1] + PRICEBYPERIOD_LABEL_OFFSET * (4 - j)))
            axs[pos // PLOT_ROWS, pos % PLOT_COLS].annotate(f"{'R' if z[4] else 'N'}", xy = (z[0], z[1]))

        # It's time to show a new batch of plots or this is the last plot
        if state_num == offset + PLOT_ROWS * PLOT_COLS - 1 or state_num == S - 1:
            plt.tight_layout()
            plt.show()
            plt.close()
            offset += PLOT_ROWS * PLOT_COLS
    print("Successfully finished displaying plots of price path by period")

# Plot the mean of prices for each transaction one by one for each security
# transaction_limit: int        up to what transaction we want to display on the x-axis
def plotPriceByTransaction(cur, p: dict, transaction_limit: int) -> None:
    S = p["S"]
    x = range(transaction_limit)
    for state_num in range(S):
        cur.execute("SELECT * FROM prices_by_transaction WHERE state_num = ?", (state_num,))
        rows = cur.fetchall()[:transaction_limit]
        means = list(map(lambda r: r[PRICEBYTRANSACTION_MEAN_COL], rows))
        sds = list(map(lambda r: r[PRICEBYTRANSACTION_STDEV_COL], rows))
        volumes = list(map(lambda r: r[PRICEBYTRANSACTION_VOLUME_COL], rows))

        plt.plot(means)
        plt.title(f"Transaction prices of security {state_num}")
        plt.xlabel("Transaction number")
        plt.ylabel("Price")
        plt.xticks(x)
        plt.yticks([y/10 for y in range(11)])

        means_label = map(lambda m: round(m, MEANS_ROUND), means)
        sds_label = map(lambda s: round(s, STDEV_ROUND), sds)
        # We annotate from top to bottom: mean, standard deviation, volume
        for z in zip(x, means_label, sds_label, volumes):
            for j in range(1, len(z)):
                plt.annotate(f"{z[j]}", xy = (z[0], z[1] + PRICEBYTRANSACTION_LABEL_OFFSET * (3 - j)))
        plt.show()
        plt.clf()
    print("Successfully finished displaying plots of price path by transaction")