import streamlit as st

st.set_page_config(page_title="MarketMood AI", layout="wide")

st.title("MarketMood AI")
st.write("Financial News Sentiment Dashboard")

st.sidebar.header("Filters")
industry = st.sidebar.selectbox(
    "Select Industry",
    ["Semiconductors", "Energy"]
)

st.subheader(f"{industry} Market Sentiment")
st.info("AI-powered financial news analysis coming soon!")
