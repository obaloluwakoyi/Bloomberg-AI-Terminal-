# test_env.py
from transformers import pipeline

print("Loading a lightweight sentiment model to test environment...")
# This will download a small default model just to check your installation
classifier = pipeline("sentiment-analysis")

result = classifier("Apple shares surge after smashing earnings expectations!")[0]
print("\n--- Test Result ---")
print(f"Text: Apple shares surge after smashing earnings expectations!")
print(f"Label: {result['label']}, Score: {result['score']:.4f}")