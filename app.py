import streamlit as st
import pandas as pd
import plotly.express as px
from sentiment import analyze_sentiment

st.set_page_config(
    page_title="MarketMood AI",
    layout="wide"
)


st.markdown("""
<style>
.stApp {
    background-color: #0B1220;
    color: #FFFFFF !important;
}

[data-testid="stHeader"] {
    background-color: #0B1220;
}

[data-testid="stMetric"] {
    background-color: #172438;
    padding: 20px;
    border-radius: 10px;
}

[data-testid="stMetricLabel"],
[data-testid="stMetricValue"] {
    color: #FFFFFF !important;
}

[data-testid="stWidgetLabel"] {
    color: #FFFFFF !important;
}

h1, h2, h3, p, label {
    color: #FFFFFF !important;
}

[data-testid="stAppViewContainer"] {
    background-color: #0B1220;
}

[data-testid="stSelectbox"] label {
    color: #FFFFFF !important;
}
</style>
""", unsafe_allow_html=True)


st.title("MarketMood AI")
st.write("Financial News Sentiment & Market Mood Dashboard")
st.divider()

data = pd.read_csv("data/headlines.csv")

industry = st.selectbox(
    "Select Industry",
    sorted(data["industry"].dropna().unique())
)

date = st.selectbox(
    "Select Date",
    sorted(data["date"].unique())
)

filtered = data[
    (data["industry"] == industry) &
    (data["date"] == date)
]

with st.spinner("Analyzing headlines..."):
    results = [
        analyze_sentiment(headline)
        for headline in filtered["headline"]
    ]

df = pd.DataFrame(results)

if df.empty:
    st.warning("No headlines found.")
    st.stop()

mood_score = df["mood_score"].mean()
total = len(df)

if mood_score > 0.05:
    mood = "Positive"
elif mood_score < -0.05:
    mood = "Negative"
else:
    mood = "Neutral"

st.subheader(f"{industry} Market Overview")

col1, col2 = st.columns(2)

with col1:
    st.metric("Market Mood Score", f"{mood_score:+.2f}")
    st.caption(mood)

with col2:
    st.metric("Headlines Analyzed", total)

st.caption(
    "Scores range from -1 to +1. "
    "Positive scores show positive news sentiment, "
    "negative scores show negative sentiment, "
    "and scores near zero show neutral or mixed sentiment."
)

st.divider()

st.subheader("Sentiment Breakdown")

counts = df["sentiment"].str.lower().value_counts()

chart_data = pd.DataFrame({
    "Sentiment": ["Positive", "Neutral", "Negative"],
    "Headlines": [
        counts.get("positive", 0),
        counts.get("neutral", 0),
        counts.get("negative", 0)
    ]
})

fig = px.bar(
    chart_data,
    x="Sentiment",
    y="Headlines",
    color="Sentiment",
    color_discrete_map={
        "Positive": "#22C55E",
        "Neutral": "#94A3B8",
        "Negative": "#EF4444"
    }
)

fig.update_layout(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    showlegend=False
)

fig.update_yaxes(dtick=1)

st.plotly_chart(fig, use_container_width=True)

st.subheader("Headline Analysis")

st.dataframe(
    df[["headline", "sentiment"]],
    use_container_width=True,
    hide_index=True
)
