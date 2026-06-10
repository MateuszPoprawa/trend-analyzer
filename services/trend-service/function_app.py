import json
import logging
import os
from collections import defaultdict, Counter

import azure.functions as func
from azure.servicebus import ServiceBusClient, ServiceBusMessage
from azure.cosmos import CosmosClient

app = func.FunctionApp()

# =========================
# ENV
# =========================
SERVICE_BUS_CONN = os.environ["SERVICE_BUS_CONNECTION"]
OUTPUT_TOPIC = "trends"

COSMOS_URI = os.environ["COSMOS_URI"]
COSMOS_KEY = os.environ["COSMOS_KEY"]
DB_NAME = "trenddb"
CONTAINER_NAME = "trends"

# =========================
# COSMOS CLIENT
# =========================
cosmos_client = CosmosClient(COSMOS_URI, COSMOS_KEY)
container = cosmos_client.get_database_client(DB_NAME).get_container_client(CONTAINER_NAME)

# =========================
# SERVICE BUS TRIGGER
# =========================
@app.service_bus_topic_trigger(
    arg_name="msg",
    topic_name="analysis-results",
    subscription_name="trend-subscription",
    connection="SERVICE_BUS_CONNECTION"
)
def trend_service(msg: func.ServiceBusMessage):

    logging.info("Trend Service triggered")

    data = json.loads(msg.get_body().decode("utf-8"))

    topic = data["topic"]
    analysis = data["analysis"]

    # =========================
    # AGGREGATION STRUCTURES
    # =========================
    keyword_counter = Counter()
    sentiment_scores = []

    for item in analysis:

        # keywords
        for kw in item.get("key_phrases", []):
            keyword_counter[kw.lower()] += 1

        # sentiment
        score = convert_sentiment(item.get("sentiment"))
        sentiment_scores.append(score)

    # =========================
    # BUILD TREND RESULT
    # =========================
    top_keywords = keyword_counter.most_common(10)

    avg_sentiment = (
        sum(sentiment_scores) / len(sentiment_scores)
        if sentiment_scores else 0
    )

    trend_result = {
        "id": topic,
        "topic": topic,
        "top_keywords": [
            {"word": k, "count": v}
            for k, v in top_keywords
        ],
        "avg_sentiment": avg_sentiment,
        "articles_count": len(analysis),
    }

    # =========================
    # SAVE TO COSMOS DB
    # =========================
    container.upsert_item(trend_result)

# =========================
# SENTIMENT NORMALIZATION
# =========================
def convert_sentiment(sentiment: str):
    if sentiment == "positive":
        return 1
    elif sentiment == "neutral":
        return 0.5
    elif sentiment == "negative":
        return 0
    return 0.5


# =========================
# HTTP Endpoint
# =========================

@app.route(
    route="trends",
    methods=["GET"],
    auth_level=func.AuthLevel.ANONYMOUS
)
def get_trend(req: func.HttpRequest):

    topic = req.params.get("topic")

    if not topic:
        return func.HttpResponse(
            "Missing topic parameter",
            status_code=400
        )

    try:

        item = container.read_item(
            item=topic,
            partition_key=topic
        )

        return func.HttpResponse(
            body=json.dumps(item),
            mimetype="application/json",
            status_code=200
        )

    except Exception as e:
        return func.HttpResponse(
            body=json.dumps({
                "status": "processing"
            }),
            mimetype="application/json",
            status_code=404
        )