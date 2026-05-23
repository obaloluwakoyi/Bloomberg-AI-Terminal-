# src/analyst.py
import database as db
import pandas as pd

class AIAccountAnalyst:
    def __init__(self):
        pass

    def generate_intelligence_briefing(self):
        """
        Parses live database state pools and synthesizes an executive,
        actionable portfolio overview, shielding against unhandled empty-state breaks.
        """
        try:
            # Gather fresh architectural states from WAL layer
            state = db.load_account_state()
            transactions = db.load_transaction_logs()
            closed_trades = db.load_closed_trades()
            
            cash = state.get("capital", 0.0)
            portfolio = state.get("portfolio", {})
            cost_basis = state.get("cost_basis", {})
            
            # 1. Structural Allocations
            active_positions_count = sum(1 for q in portfolio.values() if q > 0)
            
            # Static mock pricing matrix synced to production modules
            mock_prices = {"AAPL": 175.20, "NVDA": 850.40, "MSFT": 415.10, "AMZN": 178.40, "TSLA": 170.10, "TLT": 92.10, "XHB": 112.50}
            portfolio_value = sum(qty * mock_prices.get(ticker, 100.00) for ticker, qty in portfolio.items() if qty > 0)
            total_net_worth = cash + portfolio_value
            
            cash_utilization_ratio = (portfolio_value / total_net_worth * 100) if total_net_worth > 0 else 0.0
            
            # 2. Performance Tracking Data Metrics
            total_exits = len(closed_trades)
            wins = sum(1 for t in closed_trades if t.get("realized_pnl", 0.0) > 0)
            win_rate = (wins / total_exits * 100) if total_exits > 0 else 0.0
            total_realized_pnl = sum(t.get("realized_pnl", 0.0) for t in closed_trades)
            
            # ==============================================================================
            # DETERMINISTIC REASONING MATRIX (EMBEDDED COGNITIVE ANALYST LAYER)
            # ==============================================================================
            report = []
            report.append("### 🎙️ AI Executive Investment Briefing\n")
            
            # Section A: Liquidity & Asset Allocation Health Breakdown
            report.append("#### 💳 Liquidity & Deployment Allocation Strategy")
            if cash_utilization_ratio == 0:
                report.append(f"* **Defensive Cash Stance:** The terminal is currently holding **100% flat cash reserves** (${cash:,.2f}). The background core is selectively filtering market feed entry points to avoid volatility traps.")
            elif cash_utilization_ratio > 75:
                report.append(f"* **Aggressive Capital Concentration:** Asset utilization is running hot at **{cash_utilization_ratio:.1f}%**. Capital reserves are heavily deployed in open positions. Monitor stop-loss levels closely to protect account health.")
            else:
                report.append(f"* **Balanced Deployment Matrix:** The system is maintaining a healthy balance: **{cash_utilization_ratio:.1f}%** allocated to active equities (${portfolio_value:,.2f}) and **{100-cash_utilization_ratio:.1f}%** kept liquid inside account reserves (${cash:,.2f}).")
                
            # Section B: Execution & Trend Behavior Summary
            report.append("\n#### 📊 Alpha Generation & Execution Efficiency")
            if total_exits == 0:
                report.append("* **Observation Mode Active:** No closed trade exit markers have been recorded in the performance ledger yet. Position entries are determined by NLP confidence scores exceeding your baseline threshold filters.")
            else:
                pnl_status = "Positive Alpha" if total_realized_pnl >= 0 else "Net Drawdown"
                report.append(f"* **Performance Diagnostics:** The execution strategy shows a **{win_rate:.1f}% Win Rate** across `{total_exits}` historical cycles. Closed trade actions have generated a net performance profile of **${total_realized_pnl:+,.2f}** ({pnl_status}).")
            
            # Section C: Real-Time Tactical Risk Assessment
            report.append("\n#### 🛡️ Automated Risk Assessment & Immediate Outlook")
            if active_positions_count > 0:
                report.append(f"* **Risk Warning (Open Positions):** Currently tracking `{active_positions_count}` active stock holdings. The core execution block is constantly evaluating live data feeds against your **8.0% Take-Profit** and **4.0% Stop-Loss** boundaries to protect the vault.")
                
                # Check for specific asset concentrations
                max_ticker = max(portfolio, key=lambda k: portfolio[k] * mock_prices.get(k, 100.00)) if portfolio else None
                if max_ticker and (portfolio[max_ticker] * mock_prices.get(max_ticker, 100.00) / total_net_worth) > 0.4:
                    report.append(f"* **Concentration Risk Alert:** Portfolio exposure is heavily weighted toward **{max_ticker}**. High asset concentration increases exposure to stock-specific volatility gaps.")
            else:
                report.append("* **Protected Stance:** Zero exposure to active equity variance. Your balance is safe from unexpected market crashes or negative news flows.")
                
            return "\n".join(report)
            
        except Exception as err:
            return f"⚠️ **AI Analyst Engine Interrupted:** Unable to parse active state telemetry arrays safely. Details: {str(err)}"