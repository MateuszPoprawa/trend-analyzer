import os
import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import time

# =========================
# CONFIG
# =========================

QUERY_URL = os.getenv("QUERY_SERVICE_URL")
TREND_URL = os.getenv("TREND_SERVICE_URL")

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

topic = st.text_input(
    "Wpisz temat (np. AI, Tesla, Cybersecurity):"
)

refresh = st.button("Analizuj temat")

# =========================
# START PIPELINE
# =========================

if refresh and topic:

    with st.spinner("Uruchamianie analizy..."):

        query_response = requests.post(
            QUERY_URL,
            json={"topic": topic},
            timeout=60
        )

        if query_response.status_code not in [200, 202]:
            st.error(
                f"Błąd Query Service: {query_response}"
            )
            st.stop()

    st.success("Analiza uruchomiona")

    # =========================
    # WAIT FOR PROCESSING
    # =========================

    with st.spinner(
        "Przetwarzanie newsów przez NLP Service..."
    ):

        data = None

        for _ in range(15):

            try:
                response = requests.get(
                    TREND_URL,
                    params={"topic": topic},
                    timeout=30
                )

                if response.status_code == 200:
                    data = response.json()
                    break

            except Exception:
                pass

            time.sleep(5)

        if data is None:
            st.error(
                "Nie znaleziono jeszcze wyników analizy."
            )
            st.stop()

    st.success("Dane załadowane!")

    # =========================
    # METRICS
    # =========================

    col1, col2, col3 = st.columns(3)

    col1.metric("Temat", data["topic"])
    col2.metric(
        "Liczba artykułów",
        data["articles_count"]
    )
    col3.metric(
        "Średni sentyment",
        f"{data['avg_sentiment']:.2f}"
    )

    st.divider()
    st.subheader("📝 AI Summary")
    st.info(data["summary"])

    st.divider()
    # =========================
    # KEYWORDS
    # =========================

    st.subheader("🔥 Najważniejsze trendy")

    df = pd.DataFrame(data["top_keywords"])

    fig = px.bar(
        df,
        x="word",
        y="count",
        title="Top keywords w newsach"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.divider()

    # =========================
    # SENTIMENT
    # =========================

    st.subheader("📈 Analiza sentymentu")

    sentiment = data["avg_sentiment"]

    if sentiment > 0.65:
        st.success("Dominują pozytywne newsy 👍")
    elif sentiment > 0.4:
        st.warning("Sentyment mieszany 😐")
    else:
        st.error("Dominują negatywne newsy ⚠️")

    st.progress(float(sentiment))

    st.divider()

    # =========================
    # RAW JSON
    # =========================

    st.subheader("📋 Szczegóły trendu")
    st.json(data)