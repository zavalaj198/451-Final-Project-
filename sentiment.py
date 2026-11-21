from functools import lru_cache
from transformers import pipeline


@lru_cache(maxsize=1)
def load_model():
    return pipeline(
        "text-classification",
        model="ProsusAI/finbert",
        top_k=None,
        device=-1
    )


def analyze_sentiment(headline):
    model = load_model()
    predictions = model(headline, truncation=True)[0]

    scores = {
        item["label"].lower(): item["score"]
        for item in predictions
    }

    sentiment = max(scores, key=scores.get)

    return {
        "headline": headline,
        "sentiment": sentiment,
        "positive": scores["positive"],
        "negative": scores["negative"],
        "neutral": scores["neutral"],
        "mood_score": scores["positive"] - scores["negative"]
    }
