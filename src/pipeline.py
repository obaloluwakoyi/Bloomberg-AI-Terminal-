# src/pipeline.py
import hashlib
import random

class FinancialNewsPipeline:
    def __init__(self):
        self.processed_hashes = set()

    def fetch_latest_news(self):
        pool = [
            {"headline": "[CNBC] Apple revenue beats street expectations amid massive consumer demand shift", "ticker": "AAPL"},
            {"headline": "[CNBC] Nvidia graphics card architectures surge globally to support deep computing", "ticker": "NVDA"},
            {"headline": "[CNBC] Mortgage rates jump to highest level since March on hotter inflation reports", "ticker": "XHB"},
            {"headline": "[CNBC] Microsoft cloud infrastructure expansion records triple-digit market profit gains", "ticker": "MSFT"},
            {"headline": "[CNBC] Tesla production volume declines sharply following regulatory supply chain misses", "ticker": "TSLA"},
            {"headline": "[CNBC] Bond yields fall to historical lows as macro indicators flash economic risk alert", "ticker": "TLT"}
        ]
        return random.sample(pool, k=random.randint(1, 2))

    def parse_news(self, raw_payloads):
        parsed_batch = []
        for item in raw_payloads:
            news_id = hashlib.md5(item["headline"].encode('utf-8')).hexdigest()
            parsed_batch.append({
                "news_id": news_id,
                "headline": item["headline"],
                "ticker": item["ticker"],
                "is_new_signal": news_id not in self.processed_hashes
            })
        return parsed_batch

    def commit_hash_to_memory(self, news_id):
        self.processed_hashes.add(news_id)