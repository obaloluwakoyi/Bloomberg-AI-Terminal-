# src/app.py
import streamlit as st
import pandas as pd
import database as db
import time
import math
from intelligence_panel import MultiModelIntelligencePanel
from notifier import MailjetNotifier  # Import the custom network notifier module

st.set_page_config(
    page_title="Bloomberg AI Enterprise Terminal v6",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("📊 Bloomberg AI Terminal (Asynchronous Production Instance)")
st.markdown("---")

# Initialize SQLite internal accounting parameters
db.init_db(50000.00)
account_state = db.load_account_state()
panel_engine = MultiModelIntelligencePanel()

mock_live_prices = {"AAPL": 175.20, "NVDA": 850.40, "MSFT": 415.10, "AMZN": 178.40, "TSLA": 170.10, "TLT": 92.10, "XHB": 112.50}

# ==============================================================================
# PARAMETER SIDEBAR CONTROL & DYNAMIC MULTI-MODEL CREDENTIAL MATRIX
# ==============================================================================
st.sidebar.header("💳 System Controls & Liquidity")

st.sidebar.subheader("💰 Live Capital Management")
capital_input = st.sidebar.number_input("Target Modifier Volume ($)", min_value=100.0, max_value=250000.0, value=5000.0, step=500.0)

col_add, col_rem = st.sidebar.columns(2)
if col_add.button("🟢 Inject Capital", use_container_width=True):
    db.modify_capital_in_db(capital_input, action_type="ADD")
    st.sidebar.success(f"Injected +${capital_input:,.2f}")
    time.sleep(0.8)
    st.rerun()

if col_rem.button("🔴 Remove Capital", use_container_width=True):
    current_cash_pool = db.load_account_state()["capital"]
    if capital_input <= current_cash_pool:
        db.modify_capital_in_db(capital_input, action_type="REMOVE")
        st.sidebar.warning(f"Extracted -${capital_input:,.2f}")
        time.sleep(0.8)
        st.rerun()
    else:
        st.sidebar.error("Insufficient liquidity to execute extraction.")

st.sidebar.markdown("---")
st.sidebar.subheader("🧠 Multi-Model Intelligence Panel")

# Provider Selection Dropdown Grid
ai_provider = st.sidebar.selectbox(
    "Active Analytical AI Provider",
    ["Zero-API Local Core", "OpenAI", "Google Gemini", "Groq Acceleration", "Ollama (Local Offline)"]
)

user_api_key = ""
ollama_endpoint = "http://localhost:11434"
ollama_model_name = "llama3"

# Conditionally render input configurations based on provider requirements
if ai_provider in ["OpenAI", "Google Gemini", "Groq Acceleration"]:
    user_api_key = st.sidebar.text_input(f"Enter Custom {ai_provider} API Key", type="password")
elif ai_provider == "Ollama (Local Offline)":
    ollama_endpoint = st.sidebar.text_input("Ollama Base Local Endpoint", value="http://localhost:11434")
    ollama_model_name = st.sidebar.text_input("Target Local Model Tag", value="llama3")

# ==============================================================================
# 📬 MAILJET NOTIFICATION CONSOLE (PERSISTENT STATE STORAGE)
# ==============================================================================
st.sidebar.markdown("---")
st.sidebar.subheader("📬 Mailjet Notification Console")

# Prevent keys from dropping on 5-second asynchronous container loop refreshes
if "mj_key" not in st.session_state: st.session_state.mj_key = ""
if "mj_secret" not in st.session_state: st.session_state.mj_secret = ""
if "mj_email" not in st.session_state: st.session_state.mj_email = ""

mj_key_input = st.sidebar.text_input("Mailjet API Key", value=st.session_state.mj_key, type="password")
mj_secret_input = st.sidebar.text_input("Mailjet Secret Key", value=st.session_state.mj_secret, type="password")
mj_email_input = st.sidebar.text_input("Verified Sender/Receiver Email", value=st.session_state.mj_email)

# Map live inputs back into background memory state caches
st.session_state.mj_key = mj_key_input
st.session_state.mj_secret = mj_secret_input
st.session_state.mj_email = mj_email_input

# Instantiating the notifier engine matching credentials
notifier_engine = MailjetNotifier(
    api_key=st.session_state.mj_key,
    secret_key=st.session_state.mj_secret,
    sender_email=st.session_state.mj_email
)

if notifier_engine.is_configured():
    st.sidebar.success("🟢 Mailjet Alert Matrix Armed")
else:
    st.sidebar.info("💡 Enter Mailjet keys to activate email notifications.")

st.sidebar.markdown("---")
if st.sidebar.button("⚠️ Emergency Flush & Clear History", use_container_width=True):
    db.clear_all_tables(50000.00)
    st.sidebar.warning("Database records flushed. Capital re-anchored to $50,000.00.")
    time.sleep(0.8)
    st.rerun()

# ==============================================================================
# READ CURRENT METRICS FROM WAL SOURCE
# ==============================================================================
capital = account_state["capital"]
portfolio = account_state["portfolio"]
cost_basis = account_state["cost_basis"]
transaction_logs = db.load_transaction_logs()
closed_trades = db.load_closed_trades()

current_open_value = sum(qty * mock_live_prices.get(t, 100.00) for t, qty in portfolio.items() if qty > 0)
net_worth = round(capital + current_open_value, 2)

total_exits = len(closed_trades)
win_rate = 100.0
profit_factor = 0.0
sharpe_ratio_edge = 0.00

if total_exits > 0:
    wins = sum(1 for t in closed_trades if t["realized_pnl"] > 0)
    win_rate = round((wins / total_exits) * 100, 1)
    gross_profits = sum(t["realized_pnl"] for t in closed_trades if t["realized_pnl"] > 0)
    gross_losses = abs(sum(t["realized_pnl"] for t in closed_trades if t["realized_pnl"] < 0))
    profit_factor = round(gross_profits / gross_losses, 2) if gross_losses > 0 else round(gross_profits, 2)
    
    returns = [t["return_pct"] for t in closed_trades]
    avg_ret = sum(returns) / len(returns)
    if len(returns) > 1:
        var_ret = sum((r - avg_ret) ** 2 for r in returns) / (len(returns) - 1)
        std_ret = math.sqrt(var_ret)
        sharpe_ratio_edge = round(avg_ret / std_ret, 2) if std_ret > 0 else 0.00
    else:
        sharpe_ratio_edge = round(avg_ret / 0.05, 2)

# ==============================================================================
# UI RENDERING LAYOUT
# ==============================================================================
m1, m2, m3 = st.columns(3)
m1.metric("Available Account Liquidity", f"${capital:,.2f}")
m2.metric("Total Vault Net Worth Valuation", f"${net_worth:,.2f}")
m3.metric("Closed Signal Trade Exits", f"{total_exits:,}")

st.write("### 📈 Institutional Risk & Strategy Telemetry")
t1, t2, t3 = st.columns(3)
t1.metric("Strategy Win Rate", f"{win_rate}%")
t2.metric("Profit Factor Edge", f"{profit_factor}")
t3.metric("Calculated Sharpe Ratio", f"{sharpe_ratio_edge}")

# ==============================================================================
# STREAM DYNAMIC MULTI-PROVIDER BRIEFINGS DIRECT TO PANEL
# ==============================================================================
st.markdown("---")
with st.spinner(f"Requesting dynamic structural briefing synthesis via {ai_provider}..."):
    briefing_markdown = panel_engine.generate_briefing(
        provider=ai_provider,
        api_key=user_api_key,
        ollama_url=ollama_endpoint,
        ollama_model=ollama_model_name
    )
st.info(briefing_markdown)

st.markdown("---")
pane_left, pane_right = st.columns([2, 1])

with pane_left:
    st.write("### 📜 Consolidated Transaction Audit Trail Logs")
    if transaction_logs:
        st.dataframe(pd.DataFrame(transaction_logs), use_container_width=True, hide_index=True)
    else:
        st.info("Awaiting structural execution updates from the running background worker...")

with pane_right:
    st.write("### 💼 Active Portfolio Open Positions")
    positions_data = []
    for t, q in portfolio.items():
        if q > 0:
            total_cost = cost_basis.get(t, 0.0)
            avg_entry = total_cost / q if q > 0 else 0.0
            positions_data.append({
                "Ticker": t, 
                "Shares Owned": f"{q:,}", 
                "Avg Entry": f"${avg_entry:,.2f}",
                "Est. Value": f"${(q * mock_live_prices.get(t, 100.00)):,.2f}"
            })
    if positions_data:
        st.dataframe(pd.DataFrame(positions_data), use_container_width=True, hide_index=True)
    else:
        st.info("Portfolio currently holding 100% stable cash liquidity reserves.")

# Rerun the interface container safely to refresh metric logs
time.sleep(5)
st.rerun()