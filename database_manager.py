def createTransactionsTable(cur) -> None:
    cur.execute("DROP TABLE IF EXISTS transactions")
    cur.execute('''
        CREATE TABLE transactions (
            period_num INT NOT NULL,
            iteration_num INT NOT NULL,
            state_num INT NOT NULL,
            transaction_num INT NOT NULL,
            buyer_id INT NOT NULL,
            seller_id INT NOT NULL,
            price REAL NOT NULL,
            action INT NOT NULL
        );
    ''')

# Stores what states realized during each period
def createRealizationsTable(cur) -> None:
    cur.execute("DROP TABLE IF EXISTS realizations")
    cur.execute('''
        CREATE TABLE realizations (
            period_num INT NOT NULL,
            state_num INT NOT NULL,
            realized INT
        )
    ''')

def updateRealizationsTable(cur, period_num: int, S: int, R) -> None:
    for state_num in range(S):
        cur.execute("INSERT INTO realizations VALUES (?, ?, ?)",
                    [period_num, state_num, 1 if state_num in R else 0])

def createAgentsTable(cur) -> None:
    cur.execute("DROP TABLE IF EXISTS agents")
    cur.execute('''
        CREATE TABLE agents (
            period_num INT NOT NULL,
            agent_num INT NOT NULL,
            num_states INT NOT NULL,
            balance REAL NOT NULL,
            states TEXT NOT NULL,
            not_info TEXT NOT NULL,
            C INT NOT NULL
        )
    ''')

# small_worlds: List[SmallWorld]
def updateAgentsTable(cur, period_num: int, small_worlds) -> None:
    for sw in small_worlds:
        states = ",".join(map(str, sw.states.keys()))
        not_info = ",".join(map(str, sw.not_info))
        cur.execute("INSERT INTO agents VALUES (?, ?, ?, ?, ?, ?, ?)",
                    [period_num, sw.agent_num, sw.num_states, sw.balance, states, not_info, sw.C])

def createPricesByPeriodTable(cur) -> None:
    cur.execute("DROP TABLE IF EXISTS prices_by_period")
    cur.execute('''
        CREATE TABLE prices_by_period (
            state_num INT NOT NULL,
            period_num INT NOT NULL,
            mean INT,
            st_dev INT,
            volume INT NOT NULL,
            realized INT
        )
    ''')

def createPricesByTransactionTable(cur) -> None:
    cur.execute("DROP TABLE IF EXISTS prices_by_transaction")
    cur.execute('''
        CREATE TABLE prices_by_transaction (
            state_num INT NOT NULL,
            transaction_num INT NOT NULL,
            mean INT,
            st_dev INT,
            volume INT NOT NULL
        )
    ''')