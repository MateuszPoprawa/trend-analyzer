import os
import streamlit as st
import requests
import time
import uuid

# =========================
# CONFIG
# =========================

QUERY_URL = os.getenv("QUERY_SERVICE_URL")
SUMMARY_URL = os.getenv("SUMMARY_SERVICE_URL")

st.set_page_config(
    page_title="Summary Generator Dashboard",
    layout="wide"
)

# =========================
# HEADER
# =========================

st.title("📊 Summary Generator Dashboard")

# =========================
# INPUT
# =========================

url = st.text_input(
    "Enter url:"
)

refresh = st.button("Generate summary")

# =========================
# START PIPELINE
# =========================

if refresh and url:
    id = str(uuid.uuid4())
    with st.spinner("Generating  summary..."):
        id = str(uuid.uuid4())
        query_response = requests.post(
            QUERY_URL,
            json={"id": id,
                   "url": url},
            timeout=60
        )

        if query_response.status_code not in [200, 202]:
            st.error(
                f"Error Query Service: {query_response}"
            )
            st.stop()

    st.success("Summary generation started.")

    # =========================
    # WAIT FOR PROCESSING
    # =========================

    with st.spinner(""):

        data = None

        for _ in range(15):

            try:
                response = requests.get(
                    SUMMARY_URL,
                    params={"id": id, "url": url},
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
                "Error occurred."
            )
            st.stop()

    st.success("Summary generated!")
    
    with st.container():
        st.write(data["summary"])
    