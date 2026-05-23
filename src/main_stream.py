# src/main_stream.py
import time
from pipeline import FinancialNewsPipeline
from model import FinancialSentimentAnalyzer

def run_bloomberg_simulation():
    print("==================================================")
    print("  LAUNCHING BLOOMBERG AI SENTIMENT TERMINAL       ")
    print("==================================================")
    
    # 1. Initialize our data pipeline and AI brain modules
    pipeline = FinancialNewsPipeline()
    analyzer = FinancialSentimentAnalyzer()
    
    print("\n[System Initialization Complete] Fetching live market feeds...\n")
    
    # 2. Pull live data from our pipeline
    raw_data = pipeline.fetch_latest_news()
    articles = pipeline.parse_news(raw_data)
    
    if not articles:
        print("[-] No articles found or terminal feed offline.")
        return

    print(f"[+] Discovered {len(articles)} fresh headlines hitting the wire.")
    print("Processing stream in real-time...\n")
    print(f"{'TICKER':<10} | {'SENTIMENT':<10} | {'CONFIDENCE':<10} | {'HEADLINE'}")
    print("-" * 80)
    
    # 3. Stream the headlines through the AI model one by one
    for article in articles:
        headline = article['headline']
        ticker = article['ticker']
        
        # Run AI sentiment scoring
        analysis = analyzer.analyze_headline(headline)
        
        sentiment = analysis['sentiment']
        confidence = f"{analysis['confidence']:.2%}"
        
        # Truncate headline for clean table output if too long
        display_headline = headline if len(headline) < 60 else f"{headline[:57]}..."
        
        # Print out formatted feed lines
        print(f"{ticker:<10} | {sentiment:<10} | {confidence:<10} | {display_headline}")
        
        # Short pause to simulate a real high-frequency terminal feed ticking in
        time.sleep(0.5)

if __name__ == "__main__":
    run_bloomberg_simulation()