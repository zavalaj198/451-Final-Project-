import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from datetime import datetime, timedelta
from sentiment import analyze_sentiment

st.set_page_config(
    page_title="MarketMood AI",
    layout="wide"
)

st.markdown("""
<style>
.stApp {
    background-color: #FFFFFF;
    color: #1F2937;
}

[data-testid="stSidebar"] {
    background-color: #F0FDF4;
}

[data-testid="stMetric"] {
    background-color: #DCFCE7;
    padding: 18px;
    border: 1px solid #86EFAC;
    border-radius: 12px;
}

[data-testid="stMetricLabel"],
[data-testid="stMetricValue"] {
    color: #166534;
}

h1, h2, h3 {
    color: #14532D !important;
}

div.stButton > button {
    background-color: #16A34A;
    color: white;
    border: none;
    border-radius: 8px;
}

.stApp p,
.stApp label {
    color: #1F2937;
}
</style>
""", unsafe_allow_html=True)


def search_news(industry):
    api_key = st.secrets["NEWS_API_KEY"]

    if industry == "Energy":
        keyword = "oil OR solar OR energy"
    else:
        keyword = "semiconductor OR chip"

    url = "https://newsapi.org/v2/everything"

    params = {
        "q": keyword,
        "apiKey": api_key,
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": 20,
        "from": (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    }

    response = requests.get(url, params=params, timeout=15)
    response.raise_for_status()

    articles = response.json()["articles"]

    return pd.DataFrame([
        {
            "headline": article["title"],
            "industry": industry,
            "date": article["publishedAt"][:10],
            "source": article["source"]["name"],
            "url": article["url"]
        }
        for article in articles
        if article.get("title")
    ])


st.title("MarketMood AI")
st.write("Financial News Sentiment & Market Mood Dashboard")
st.divider()

data = pd.read_csv("data/headlines.csv")

industry = st.selectbox(
    "Select Industry",
    sorted(data["industry"].dropna().unique())
)

source = st.radio(
    "Choose News Source",
    ["Sample Headlines", "Live News"]
)

if source == "Live News":
    if st.button("Search News"):
        try:
            with st.spinner("Searching for news..."):
                st.session_state["news_data"] = search_news(industry)
                st.session_state["news_industry"] = industry
        except Exception as e:
            st.error(f"Could not load news: {e}")

    if (
        "news_data" not in st.session_state
        or st.session_state.get("news_industry") != industry
    ):
        st.info("Click Search News to find articles.")
        st.stop()

    data = st.session_state["news_data"]

date = st.selectbox(
    "Select Date",
    sorted(data["date"].dropna().unique(), reverse=True)
)

filtered = data[
    (data["industry"] == industry) &
    (data["date"] == date)
]

if filtered.empty:
    st.warning("No headlines found.")
    st.stop()

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
    template="plotly_white",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    showlegend=False
)

fig.update_yaxes(dtick=1)

st.plotly_chart(fig, use_container_width=True)

st.subheader("Headline Analysis")

if source == "Live News":
    df["date"] = filtered["date"].values
    df["source"] = filtered["source"].values
    df["url"] = filtered["url"].values

    st.dataframe(
        df[["headline", "sentiment", "date", "source", "url"]],
        use_container_width=True,
        hide_index=True,
        column_config={
            "url": st.column_config.LinkColumn("Article Link")
        }
    )
else:
    st.dataframe(
        df[["headline", "sentiment"]],
        use_container_width=True,
        hide_index=True
    )
