import logging
import json
import os

import azure.functions as func
from azure.servicebus import ServiceBusClient, ServiceBusMessage

from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential

app = func.FunctionApp()

# =========================
# ENV VARIABLES
# =========================
AI_KEY = os.environ["AZURE_AI_KEY"]
AI_ENDPOINT = os.environ["AZURE_AI_ENDPOINT"]

SERVICE_BUS_CONN = os.environ["SERVICE_BUS_CONNECTION"]
OUTPUT_TOPIC = "analysis-results"

# =========================
# AZURE AI CLIENT
# =========================
def get_ai_client():
    return TextAnalyticsClient(
        endpoint=AI_ENDPOINT,
        credential=AzureKeyCredential(AI_KEY)
    )

# =========================
# SERVICE BUS TRIGGER
# =========================
@app.service_bus_topic_trigger(
    arg_name="msg",
    topic_name="articles",
    subscription_name="nlp-subscription",
    connection="SERVICE_BUS_CONNECTION"
)
def nlp_service(msg: func.ServiceBusMessage):

    logging.info("NLP Service triggered")

    try:
        data = json.loads(msg.get_body().decode("utf-8"))

        topic = data.get("topic")
        articles = data.get("articles", [])

        client = get_ai_client()

        results = []

        for article in articles:
            text = (article.get("title", "") + " " +
                    article.get("description", ""))

            if not text.strip():
                continue

            # =========================
            # 1. SENTIMENT ANALYSIS
            # =========================
            sentiment = client.analyze_sentiment(
                documents=[text]
            )[0]

            # =========================
            # 2. KEY PHRASES
            # =========================
            key_phrases = client.extract_key_phrases(
                documents=[text]
            )[0]

            # =========================
            # BUILD RESULT
            # =========================
            results.append({
                "title": article.get("title"),
                "url": article.get("url"),
                "sentiment": sentiment.sentiment,
                "sentiment_score": {
                    "positive": sentiment.confidence_scores.positive,
                    "neutral": sentiment.confidence_scores.neutral,
                    "negative": sentiment.confidence_scores.negative
                },
                "key_phrases": key_phrases.key_phrases
            })

        # =========================
        # SEND TO NEXT STEP
        # =========================
        send_to_service_bus(topic, results)

    except Exception as e:
        logging.error(str(e))


# =========================
# SERVICE BUS OUTPUT
# =========================
def send_to_service_bus(topic: str, results: list):

    client = ServiceBusClient.from_connection_string(
        conn_str=SERVICE_BUS_CONN
    )

    with client:
        sender = client.get_topic_sender(topic_name=OUTPUT_TOPIC)

        with sender:
            message = {
                "topic": topic,
                "analysis": results
            }

            sender.send_messages(
                ServiceBusMessage(json.dumps(message))
            )