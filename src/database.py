# src/database.py
import sqlite3
import pandas as pd
import json
import datetime

DB_PATH = "terminal_state.db"

def get_connection():
    """Establishes thread-safe concurrent Write-Ahead Logging (WAL) mode connections."""
    conn = sqlite3.connect(DB_PATH, timeout=30.0)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    return conn

def init_db(starting_capital=50000.00):
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS account_state (
            id INTEGER PRIMARY KEY,
            capital REAL,
            portfolio TEXT,
            cost_basis TEXT
        )''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            ticker TEXT,
            action TEXT,
            headline TEXT,
            details TEXT,
            remaining_cash REAL
        )''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS performance_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            return_pct REAL,
            realized_pnl REAL
        )''')
    
    cursor.execute("SELECT COUNT(*) FROM account_state")
    if cursor.fetchone()[0] == 0:
        cursor.execute(
            "INSERT INTO account_state (id, capital, portfolio, cost_basis) VALUES (1, ?, '{}', '{}')",
            (starting_capital,)
        )
    conn.commit()
    conn.close()

def load_account_state():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT capital, portfolio, cost_basis FROM account_state WHERE id = 1")
    row = cursor.fetchone()
    conn.close()
    if not row:
        return {"capital": 50000.00, "portfolio": {}, "cost_basis": {}}
    return {
        "capital": row[0],
        "portfolio": json.loads(row[1]),
        "cost_basis": json.loads(row[2])
    }

def save_account_state(capital, portfolio, cost_basis):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE account_state SET capital = ?, portfolio = ?, cost_basis = ? WHERE id = 1",
        (capital, json.dumps(portfolio), json.dumps(cost_basis))
    )
    conn.commit()
    conn.close()

def modify_capital_in_db(amount, action_type="ADD"):
    """
    Safely adds or extracts liquidity from the live state database 
    without closing open positions or corrupting the worker loop.
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    state = load_account_state()
    current_cap = state["capital"]
    
    if action_type == "ADD":
        new_capital = current_cap + amount
        log_details = f"Liquidity Top-Up: Injected +${amount:,.2f} into vault reserves."
        log_action = "DEPOSIT"
    else:
        new_capital = max(0.0, current_cap - amount)
        log_details = f"Liquidity Outflow: Removed -${amount:,.2f} from vault reserves."
        log_action = "WITHDRAW"
        
    cursor.execute("UPDATE account_state SET capital = ? WHERE id = 1", (new_capital,))
    
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute(
        "INSERT INTO transactions (timestamp, ticker, action, headline, details, remaining_cash) VALUES (?, 'CASH', ?, 'Manual Account Capital Adjustment', ?, ?)",
        (ts, log_action, log_details, new_capital)
    )
    conn.commit()
    conn.close()

def load_transaction_logs():
    conn = get_connection()
    try:
        df = pd.read_sql_query("SELECT timestamp, ticker, action, headline, details, remaining_cash FROM transactions ORDER BY id DESC", conn)
        logs = df.to_dict(orient="records")
    except Exception:
        logs = []
    conn.close()
    return logs

def log_closed_trade(return_pct, realized_pnl):
    conn = get_connection()
    cursor = conn.cursor()
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT INTO performance_metrics (timestamp, return_pct, realized_pnl) VALUES (?, ?, ?)", (ts, return_pct, realized_pnl))
    conn.commit()
    conn.close()

def load_closed_trades():
    conn = get_connection()
    try:
        df = pd.read_sql_query("SELECT return_pct, realized_pnl FROM performance_metrics", conn)
        trades = df.to_dict(orient="records")
    except Exception:
        trades = []
    conn.close()
    return trades

def clear_all_tables(starting_capital):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS account_state")
    cursor.execute("DROP TABLE IF EXISTS transactions")
    cursor.execute("DROP TABLE IF EXISTS performance_metrics")
    conn.commit()
    conn.close()
    init_db(starting_capital)