import pandas as pd
from sentiment_analyzer import detect_tone

df = pd.read_csv("data/processed/analysis_dataset.csv").head(75)

df['original_tone_detected'] = df['original_products'].astype(str).apply(detect_tone)
df['modified_tone_detected'] = df['modified_products'].astype(str).apply(detect_tone)

df.to_csv("data/processed/test_sentiment_75.csv", index=False)

print("Sentiment analysis completed for first 75 responses.")