# Bloomberg AI Enterprise Terminal v6 (Asynchronous Simulation Core)

An elite, high-performance financial trading terminal simulation powered by multi-model AI routing arrays and structured algorithmic execution protocols. This engine features dynamic sentiment-based automated trade processing, technical risk boundary policing, and custom transactional automated email notifications.

---

## 🚀 Key Architectural Highlights

* **Concurrent WAL State Core:** Uses SQLite Write-Ahead Logging (WAL) to enable multi-threaded read/write actions, insulating background workers and front-end interface processes against database locking.
* **Algorithmic Sizing & Protection:** Utilizes custom Kelly Criterion logic to modulate exposure scales between 2% and 15% of available liquidity while managing 8.0% Take-Profit and 4.0% Stop-Loss risk boundaries.
* **Decoupled AI Engine Router:** Implements zero-bloat network connectivity abstractions using Python's native `http.client`. Seamlessly alternate between OpenAI, Google Gemini, Groq, and local offline Ollama environments.
* **Automated Operational Alerts:** Integrates Mailjet V3.1 Send API matrices directly into execution blocks to trigger email alerts for manual capital inputs or technical position liquidations.

---

## 📂 System Directory Structure

```text
├── src/
│   ├── analyst.py              # Local deterministic analytics reporting matrix
│   ├── app.py                  # Streamlit enterprise front-end & dashboard controller
│   ├── database.py             # SQLite WAL layer schema configuration & state handlers
│   ├── intelligence_panel.py   # Native multi-LLM routing pipeline (Zero-dependency)
│   ├── notifier.py             # Mailjet notification wrapper protocol
│   ├── pipeline.py             # MD5-guarded stream ingestion & headline ingestion asset
│   └── trading_simulator.py    # Algorithmic Kelly sizing engine & risk boundary enforcer
├── terminal_state.db           # Live generated WAL SQLite database file
└── requirements.txt            # Operational python environment dependencies