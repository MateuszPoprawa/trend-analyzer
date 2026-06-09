import logging
import os
import json
import requests
from datetime import datetime, timedelta    
import azure.functions as func
from azure.servicebus import ServiceBusClient, ServiceBusMessage

app = func.FunctionApp()

# =========================
# ENV VARIABLES
# =========================
NEWS_API_KEY = os.environ["NEWS_API_KEY"]
SERVICE_BUS_CONN = os.environ["SERVICE_BUS_CONNECTION"]
TOPIC_NAME = "articles"

# =========================
# MAIN HTTP TRIGGER
# =========================
@app.route(route="query", auth_level=func.AuthLevel.ANONYMOUS)
def query_service(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Query Service triggered")

    try:
        body = req.get_json()
        topic = body.get("topic")

        if not topic:
            return func.HttpResponse(
                "Missing 'topic'",
                status_code=400
            )

        # =========================
        # 1. CALL NEWSAPI
        # =========================
        articles = fetch_news(topic)

        # =========================
        # 2. SEND TO SERVICE BUS
        # =========================
        send_to_service_bus(topic, articles)

        # =========================
        # RESPONSE
        # =========================
        return func.HttpResponse(
            json.dumps({
                "topic": topic,
                "articles_count": len(articles),
                "status": "sent_to_pipeline"
            }),
            mimetype="application/json",
            status_code=200
        )

    except Exception as e:
        logging.error(str(e))
        return func.HttpResponse(str(e), status_code=500)


# =========================
# NEWSAPI CALL
# =========================
def fetch_news(topic: str):
    from_date = (datetime.utcnow() - timedelta(days=7)).strftime("%Y-%m-%d")

    url = "https://newsapi.org/v2/everything"
    params = {
        "q": topic,
        "from": from_date,
        "language": "en",
        "pageSize": 100,
        "sortBy": "publishedAt",
        "apiKey": NEWS_API_KEY
    }

    response = requests.get(url, params=params)
    data = response.json()
    print(data)
    articles = []

    for article in data.get("articles", []):
        articles.append({
            "title": article.get("title"),
            "description": article.get("description"),
            "content": article.get("content"),
            "url": article.get("url"),
            "source": article.get("source", {}).get("name"),
            "publishedAt": article.get("publishedAt")
        })

    return articles


# =========================
# SERVICE BUS SENDER
# =========================
def send_to_service_bus(topic: str, articles: list):
    client = ServiceBusClient.from_connection_string(
        conn_str=SERVICE_BUS_CONN,
        logging_enable=True
    )

    with client:
        sender = client.get_topic_sender(topic_name=TOPIC_NAME)

        with sender:
            message = {
                "topic": topic,
                "articles": articles
            }

            sb_message = ServiceBusMessage(json.dumps(message))

            sender.send_messages(sb_message)