import os
import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import time
import uuid

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
        id = str(uuid.uuid4())
        query_response = requests.post(
            QUERY_URL,
            json={"id": id,
                   "url": topic},
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
                    params={"id": id},
                    timeout=30
                )

                if response.status_code == 200:
                    data = response.json()
                    break

            except Exception:
                pass

            time.sleep(20)

        if data is None:
            st.error(
                "Nie znaleziono jeszcze wyników analizy."
            )
            st.stop()

    st.success("Dane załadowane!")
    
    st.write(data["summary"])
    