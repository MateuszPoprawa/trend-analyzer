import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import time

# =========================
# CONFIG
# =========================
API_URL = "http://localhost:7071/api/trends"  # Trend Service endpoint

st.set_page_config(
    page_title="Trend Analyzer Dashboard",
    layout="wide"
)

# =========================
# HEADER
# =========================
st.title("📊 News Trend Analyzer Dashboard")
st.caption("Azure + NewsAPI + AI-powered trend analysis")

# =========================
# INPUT
# =========================
topic = st.text_input("Wpisz temat (np. AI, Tesla, Cybersecurity):")

refresh = st.button("Pobierz trendy")

# =========================
# FETCH DATA
# =========================
if refresh and topic:

    with st.spinner("Pobieranie danych z Cosmos DB..."):

        response = requests.get(API_URL, params={"topic": topic})

        if response.status_code != 200:
            st.error("Błąd pobierania danych")
            st.stop()

        data = response.json()

    st.success("Dane załadowane!")

    # =========================
    # METRICS ROW
    # =========================
    col1, col2, col3 = st.columns(3)

    col1.metric("Temat", data["topic"])
    col2.metric("Liczba artykułów", data["articles_count"])
    col3.metric("Średni sentyment", f"{data['avg_sentiment']:.2f}")

    st.divider()

    # =========================
    # TOP KEYWORDS
    # =========================
    st.subheader("🔥 Najważniejsze trendy (keywords)")

    df = pd.DataFrame(data["top_keywords"])

    fig = px.bar(
        df,
        x="word",
        y="count",
        title="Top keywords w newsach"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # =========================
    # SENTIMENT VISUALIZATION
    # =========================
    st.subheader("📈 Analiza sentymentu")

    sentiment = data["avg_sentiment"]

    if sentiment > 0.65:
        st.success("Dominują pozytywne newsy 👍")
    elif sentiment > 0.4:
        st.warning("Sentyment mieszany 😐")
    else:
        st.error("Dominują negatywne newsy ⚠️")

    # gauge-like visualization
    st.progress(float(sentiment))

    st.divider()

    # =========================
    # RAW DATA TABLE
    # =========================
    st.subheader("📋 Szczegóły trendu")

    st.json(data)

    # =========================
    # AUTO REFRESH OPTION
    # =========================
    st.divider()
    auto = st.checkbox("Auto-refresh co 30s")

    if auto:
        time.sleep(30)
        st.rerun()