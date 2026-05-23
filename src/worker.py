# src/worker.py
import time
import random
import database as db
from pipeline import FinancialNewsPipeline
from model import FinancialSentimentAnalyzer
from trading_simulator import AlgorithmicExecutionEngine

def run_background_worker():
    print("🚀 Bloomberg AI Terminal: Background Worker Engine Initializing...")
    
    pipeline = FinancialNewsPipeline()
    analyzer = FinancialSentimentAnalyzer()
    
    # Check the database file state or create it safely if missing
    db.init_db(50000.00)
    trader = AlgorithmicExecutionEngine()
    
    market_prices = {
        "AAPL": 175.20, "NVDA": 850.40, "MSFT": 415.10, "AMZN": 178.40, "TSLA": 170.10, "TLT": 92.10, "XHB": 112.50
    }
    
    confidence_gating = 0.55
    tp_barrier, sl_barrier = 8.0, 4.0

    print("📡 Worker connected to data streams. Processing continuous data scans...")

    while True:
        try:
            start_time = time.time()
            
            raw_data = pipeline.fetch_latest_news()
            live_signals = pipeline.parse_news(raw_data)
            
            for signal in live_signals:
                if not signal["is_new_signal"]:
                    continue
                
                analysis = analyzer.analyze_headline(signal["headline"])
                ticker = signal["ticker"]
                
                trader.process_signal(
                    ticker=ticker,
                    sentiment=analysis["sentiment"],
                    confidence=analysis["confidence"],
                    headline=signal["headline"],
                    confidence_threshold=confidence_gating,
                    current_price=market_prices.get(ticker, 100.00)
                )
                pipeline.commit_hash_to_memory(signal["news_id"])
            
            for ticker in market_prices:
                market_prices[ticker] = round(market_prices[ticker] * (1 + random.uniform(-0.003, 0.005)), 2)
            
            trader.enforce_technical_risk_boundaries(market_prices, tp_barrier, sl_barrier)
            
            # Print state details to the console log window
            current_cash = db.load_account_state()['capital']
            print(f"⏱️ Cycle complete | Engine Cash Check: ${current_cash:,.2f}")
            time.sleep(4)
            
        except KeyboardInterrupt:
            print("\n🛑 Background Worker safely disconnected from database core.")
            break
        except Exception as e:
            print(f"⚠️ Worker Exception Sequence: {e}")
            time.sleep(5)

if __name__ == "__main__":
    run_background_worker()