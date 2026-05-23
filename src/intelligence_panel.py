# src/intelligence_panel.py
import os
import json
import http.client
import database as db

class MultiModelIntelligencePanel:
    def __init__(self):
        # Fallback system prices map
        self.mock_prices = {"AAPL": 175.20, "NVDA": 850.40, "MSFT": 415.10, "AMZN": 178.40, "TSLA": 170.10, "TLT": 92.10, "XHB": 112.50}

    def _assemble_raw_context(self):
        """Extracts and organizes the active SQLite state into a structured context payload."""
        state = db.load_account_state()
        logs = db.load_transaction_logs()[:6]  # Last 6 transactions for concise context
        closed = db.load_closed_trades()
        
        cash = state.get("capital", 0.0)
        portfolio = state.get("portfolio", {})
        cost_basis = state.get("cost_basis", {})
        
        open_value = sum(qty * self.mock_prices.get(t, 100.00) for t, qty in portfolio.items() if qty > 0)
        net_worth = cash + open_value
        
        # Calculate performance telemetry vectors
        total_exits = len(closed)
        wins = sum(1 for t in closed if t.get("realized_pnl", 0.0) > 0)
        win_rate = (wins / total_exits * 100) if total_exits > 0 else 0.0
        total_pnl = sum(t.get("realized_pnl", 0.0) for t in closed)
        
        context = {
            "account_summary": {
                "available_cash": round(cash, 2),
                "open_portfolio_value": round(open_value, 2),
                "net_worth": round(net_worth, 2),
                "cash_utilization_pct": round((open_value / net_worth * 100), 2) if net_worth > 0 else 0.0
            },
            "trading_telemetry": {
                "total_closed_trades": total_exits,
                "win_rate_pct": round(win_rate, 2),
                "total_realized_pnl": round(total_pnl, 2)
            },
            "active_positions": {t: {"shares": q, "basis": cost_basis.get(t, 0.0)} for t, q in portfolio.items() if q > 0},
            "recent_audit_trail": [{"action": l["action"], "ticker": l["ticker"], "details": l["details"]} for l in logs]
        }
        return context

    def generate_briefing(self, provider, api_key=None, ollama_url="http://localhost:11434", ollama_model="llama3"):
        """Routes execution data payloads to the selected AI provider."""
        context_data = self._assemble_raw_context()
        
        system_prompt = (
            "You are an elite Bloomberg Quant Analyst. Review the provided JSON account portfolio state, "
            "metrics telemetry, and transaction log. Generate a sharp, professional, highly technical "
            "executive market briefing in clean Markdown format. Focus heavily on asset allocation risk, "
            "capital deployment efficiency, alpha generation, and immediate risk boundary alerts. Do not output JSON."
        )
        user_prompt = f"Current Terminal State Json Payload Profile:\n{json.dumps(context_data, indent=2)}"

        # ROUTE A: OPENAI IMPLEMENTATION
        if provider == "OpenAI":
            if not api_key: return "⚠️ **OpenAI Error:** Missing API Key authentication credentials."
            return self._call_openai(api_key, system_prompt, user_prompt)

        # ROUTE B: GEMINI IMPLEMENTATION
        elif provider == "Google Gemini":
            if not api_key: return "⚠️ **Gemini Error:** Missing API Key authentication credentials."
            return self._call_gemini(api_key, system_prompt, user_prompt)

        # ROUTE C: GROQ IMPLEMENTATION
        elif provider == "Groq Acceleration":
            if not api_key: return "⚠️ **Groq Error:** Missing API Key authentication credentials."
            return self._call_groq(api_key, system_prompt, user_prompt)

        # ROUTE D: OLLAMA OFFLINE DEPLOYMENT
        elif provider == "Ollama (Local Offline)":
            return self._call_ollama(ollama_url, ollama_model, system_prompt, user_prompt)

        # ROUTE E: NO-API DETERMINISTIC STRUCTURAL FALLBACK CORE
        else:
            return self._generate_deterministic_report(context_data)

    # ==============================================================================
    # NATIVE COGNITIVE NETWORK NETWORK REQ CALLS (No External Dependency Clashes)
    # ==============================================================================
    def _call_openai(self, key, sys, user):
        try:
            conn = http.client.HTTPSConnection("api.openai.com")
            headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
            payload = json.dumps({
                "model": "gpt-4o-mini",
                "messages": [{"role": "system", "content": sys}, {"role": "user", "content": user}],
                "temperature": 0.3
            })
            conn.request("POST", "/v1/chat/completions", payload, headers)
            res = json.loads(conn.getresponse().read().decode())
            return res["choices"][0]["message"]["content"]
        except Exception as e:
            return f"⚠️ **OpenAI Gateway Timeout Error:** {str(e)}"

    def _call_gemini(self, key, sys, user):
        try:
            conn = http.client.HTTPSConnection("generativelanguage.googleapis.com")
            headers = {"Content-Type": "application/json"}
            url = f"/v1beta/models/gemini-1.5-flash:generateContent?key={key}"
            payload = json.dumps({
                "contents": [{"parts": [{"text": f"{sys}\n\n{user}"}]}],
                "generationConfig": {"temperature": 0.3}
            })
            conn.request("POST", url, payload, headers)
            res = json.loads(conn.getresponse().read().decode())
            return res["candidates"][0]["content"]["parts"][0]["text"]
        except Exception as e:
            return f"⚠️ **Gemini Gateway Timeout Error:** {str(e)}"

    def _call_groq(self, key, sys, user):
        try:
            conn = http.client.HTTPSConnection("api.groq.com")
            headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
            payload = json.dumps({
                "model": "mixtral-8x7b-32768",
                "messages": [{"role": "system", "content": sys}, {"role": "user", "content": user}],
                "temperature": 0.2
            })
            conn.request("POST", "/openai/v1/chat/completions", payload, headers)
            res = json.loads(conn.getresponse().read().decode())
            return res["choices"][0]["message"]["content"]
        except Exception as e:
            return f"⚠️ **Groq Acceleration Network Error:** {str(e)}"

    def _call_ollama(self, url, model, sys, user):
        try:
            # Clean url parsing string parameters
            clean_host = url.replace("http://", "").replace("https://", "")
            if ":" in clean_host:
                host, port = clean_host.split(":")
                port = int(port)
            else:
                host, port = clean_host, 80
                
            conn = http.client.HTTPConnection(host, port, timeout=15)
            headers = {"Content-Type": "application/json"}
            payload = json.dumps({
                "model": model,
                "system": sys,
                "prompt": user,
                "stream": False,
                "options": {"temperature": 0.3}
            })
            conn.request("POST", "/api/generate", payload, headers)
            res = json.loads(conn.getresponse().read().decode())
            return res["response"]
        except Exception as e:
            return f"⚠️ **Ollama Offline Connection Timeout:** Verify Ollama is running live on your local machine (`ollama run {model}`) at `{url}`. Details: {e}"

    def _generate_deterministic_report(self, ctx):
        """High-demand built-in reporting logic that generates analysis with zero API dependencies."""
        summary = ctx["account_summary"]
        telemetry = ctx["trading_telemetry"]
        
        report = [
            "### 🎙️ AI Executive Investment Briefing *(Deterministic Local Core)*\n",
            "#### 💳 Liquidity & Deployment Allocation Strategy",
            f"* **Capital Reserves Summary:** Available Liquidity: `${summary['available_cash']:,.2f}` | Open Exposure Valuation: `${summary['open_portfolio_value']:,.2f}`.",
            f"* **Capital Deployment Vector:** Currently maintaining a **{summary['cash_utilization_pct']}%** asset utilization exposure footprints."
        ]
        
        if summary['cash_utilization_pct'] == 0:
            report.append("* **Defensive Stance:** 100% stable cash positioning. Ready for model entry triggers.")
        elif summary['cash_utilization_pct'] > 70:
            report.append("* **Concentration Risk Warning:** Heavy capital deployment. Ensure stop-loss boundaries are strictly enforced.")
            
        report.append("\n#### 📊 Alpha Generation & Execution Efficiency")
        if telemetry['total_closed_trades'] == 0:
            report.append("* **Awaiting Exits:** Zero positions have been liquidated into the performance metrics matrix yet.")
        else:
            report.append(f"* **Performance Diagnostics:** Recorded a **{telemetry['win_rate_pct']}% Win Rate** across `{telemetry['total_closed_trades']}` historical cycles. Total captured P&L performance is **${telemetry['total_realized_pnl']:+,.2f}**.")
            
        return "\n".join(report)