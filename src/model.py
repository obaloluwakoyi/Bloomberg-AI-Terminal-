# src/model.py
import os

os.environ.setdefault("DISABLE_SAFETENSORS_CONVERSION", "1")

try:
    from transformers import AutoModelForSequenceClassification, AutoTokenizer
    from transformers import pipeline as hf_pipeline
except Exception:
    AutoModelForSequenceClassification = None
    AutoTokenizer = None
    hf_pipeline = None

class FinancialSentimentAnalyzer:
    def __init__(self):
        self.model_name = "ProsusAI/finbert"
        self.nlp = None
        self._load_model()

    def _load_model(self):
        if not all([AutoTokenizer, AutoModelForSequenceClassification, hf_pipeline]):
            return
        try:
            tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            model = AutoModelForSequenceClassification.from_pretrained(self.model_name, use_safetensors=False)
            self.nlp = hf_pipeline("sentiment-analysis", model=model, tokenizer=tokenizer)
        except Exception:
            self.nlp = None

    def _analyze_with_rules(self, headline):
        text = headline.upper()
        bull_words = {"BEAT", "SURGE", "RALLY", "GAIN", "GROWTH", "UPGRADE", "PROFIT", "RECORD", "STRONG"}
        bear_words = {"MISS", "DROP", "FALL", "DOWNGRADE", "LOSS", "WEAK", "CUT", "DECLINE", "RISK"}
        
        bull_hits = sum(w in text for w in bull_words)
        bear_hits = sum(w in text for w in bear_words)
        
        if bull_hits > bear_hits:
            return {"sentiment": "BULLISH", "confidence": round(min(0.60 + 0.1*(bull_hits-bear_hits), 0.95), 4)}
        if bear_hits > bull_hits:
            return {"sentiment": "BEARISH", "confidence": round(min(0.60 + 0.1*(bear_hits-bull_hits), 0.95), 4)}
        return {"sentiment": "NEUTRAL", "confidence": 0.5000}

    def analyze_headline(self, headline):
        if not headline or not str(headline).strip():
            return {"sentiment": "NEUTRAL", "confidence": 0.5000}
        if self.nlp is None:
            return self._analyze_with_rules(headline)
        try:
            res = self.nlp(headline)[0]
            label_map = {"positive": "BULLISH", "negative": "BEARISH", "neutral": "NEUTRAL"}
            return {"sentiment": label_map.get(res["label"].lower(), "NEUTRAL"), "confidence": round(res["score"], 4)}
        except Exception:
            return self._analyze_with_rules(headline)