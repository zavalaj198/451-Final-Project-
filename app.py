import streamlit as st
import pandas as pd
from sentiment import analyze_sentiment

st.set_page_config(page_title="MarketMood AI")
st.title("MarketMood AI")

data = pd.read_csv("data/headlines.csv")

industry = st.selectbox(
    "Select Industry", data["industry"].unique()
)

filtered = data[data["industry"] == industry]

results = [analyze_sentiment(h) for h in filtered["headline"]]
df = pd.DataFrame(results)

st.subheader(f"{industry} Market Sentiment")
st.metric("Market Mood Score", round(df["mood_score"].mean(), 2))

st.bar_chart(df["sentiment"].value_counts())
st.dataframe(df[["headline", "sentiment"]])

st.caption("Demo testing")
