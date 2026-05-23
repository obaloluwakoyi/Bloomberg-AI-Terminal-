# src/trading_simulator.py
import re
import database as db

class AlgorithmicExecutionEngine:
    def __init__(self):
        pass

    def _sanitize(self, t):
        return re.sub(r'\s*\d+$', '', str(t)).strip().upper()

    def calculate_kelly_size(self, confidence, price):
        """Calculates dynamic trade sizing bounded between 2% and 15% of current liquidity."""
        base_kelly = max(0.02, min(confidence * 0.12, 0.15))
        multiplier = 0.75 if price > 500.0 else 1.0
        return round(base_kelly * multiplier * 100, 2)

    # Part of src/trading_simulator.py - Update these methods to accept and trigger the notifier

    def process_signal(self, ticker, sentiment, confidence, headline, confidence_threshold, current_price, notifier=None):
        ticker = self._sanitize(ticker)
        state = db.load_account_state()
        cap, port, basis = state["capital"], state["portfolio"], state["cost_basis"]
        
        if sentiment == "BULLISH" and confidence >= confidence_threshold:
            risk_pct = self.calculate_kelly_size(confidence, current_price)
            allocated_funds = cap * (risk_pct / 100.0)
            shares_to_buy = int(allocated_funds // current_price)
            cost = shares_to_buy * current_price
            
            if shares_to_buy > 0 and cap >= cost:
                cap -= cost
                port[ticker] = port.get(ticker, 0) + shares_to_buy
                basis[ticker] = basis.get(ticker, 0.0) + cost
                db.save_account_state(cap, port, basis)
                
                details = f"Allocated {risk_pct}% risk (${cost:,.2f}) to purchase {shares_to_buy:,} units at ${current_price:,.2f}/sh."
                db.log_transaction_to_db(ticker, "BUY", headline, details, cap)
                
                # TRIGGER MAILJET NOTIFICATION IF ACTIVE
                if notifier and notifier.is_configured():
                    notifier.send_trade_alert(ticker, "BUY", headline, details)
                return True

        elif sentiment == "BEARISH" and confidence >= confidence_threshold:
            if ticker in port and port[ticker] > 0:
                shares = port[ticker]
                revenue = shares * current_price
                realized_pnl = revenue - basis[ticker]
                return_pct = realized_pnl / basis[ticker]
                
                cap += revenue
                del port[ticker]
                del basis[ticker]
                db.save_account_state(cap, port, basis)
                
                db.log_closed_trade(return_pct, realized_pnl)
                details = f"Liquidated {shares:,} shares via AI structural alert. P&L: ${realized_pnl:+,.2f} ({return_pct:+.2f}%)"
                db.log_transaction_to_db(ticker, "SELL", headline, details, cap)
                
                # TRIGGER MAILJET NOTIFICATION IF ACTIVE
                if notifier and notifier.is_configured():
                    notifier.send_trade_alert(ticker, "SELL", headline, details)
                return True
        return False

    def enforce_technical_risk_boundaries(self, price_map, tp_pct, sl_pct, notifier=None):
        state = db.load_account_state()
        cap, port, basis = state["capital"], state["portfolio"], state["cost_basis"]
        
        for ticker in list(port.keys()):
            shares = port[ticker]
            if shares <= 0: continue
            avg_entry = basis[ticker] / shares
            live_price = price_map.get(ticker, avg_entry)
            pnl_pct = ((live_price - avg_entry) / avg_entry) * 100.0
            
            trigger = None
            if pnl_pct >= tp_pct: trigger = "TAKE_PROFIT"
            elif pnl_pct <= -sl_pct: trigger = "STOP_LOSS"
            
            if trigger:
                revenue = shares * live_price
                realized_pnl = revenue - basis[ticker]
                cap += revenue
                del port[ticker]
                del basis[ticker]
                db.save_account_state(cap, port, basis)
                
                db.log_closed_trade(pnl_pct / 100.0, realized_pnl)
                details = f"RISK BARRIER EXCEEDED: {trigger} triggered at ${live_price:,.2f}. P&L: {pnl_pct:+.2f}%"
                db.log_transaction_to_db(ticker, "RISK_EXIT", "Automated technical exit barrier tripped.", details, cap)
                
                # TRIGGER MAILJET NOTIFICATION IF ACTIVE
                if notifier and notifier.is_configured():
                    notifier.send_trade_alert(ticker, "RISK_EXIT", f"Technical Risk Level Reached: {trigger}", details)