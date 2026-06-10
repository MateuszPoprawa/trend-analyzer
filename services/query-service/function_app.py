import logging
import os
import json
import requests
import trafilatura
import azure.functions as func
from azure.servicebus import ServiceBusClient, ServiceBusMessage

app = func.FunctionApp()

# =========================
# ENV VARIABLES
# =========================
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
        url = body.get("url")

        if not url:
            return func.HttpResponse(
                "Missing 'url'",
                status_code=400
            )

        downloaded = trafilatura.fetch_url(url)

        if not downloaded:
            return None

        text = trafilatura.extract(
            downloaded,
            include_comments=False,
            include_tables=False
        )

        send_to_service_bus(url, text)

        return func.HttpResponse(
            json.dumps({
                "url": url,
                "status": "sent_to_pipeline"
            }),
            mimetype="application/json",
            status_code=200
        )

    except Exception as e:
        logging.error(str(e))
        return func.HttpResponse(str(e), status_code=500)

# =========================
# SERVICE BUS SENDER
# =========================
def send_to_service_bus(url: str, text: str):
    client = ServiceBusClient.from_connection_string(
        conn_str=SERVICE_BUS_CONN,
        logging_enable=True
    )

    with client:
        sender = client.get_topic_sender(topic_name=TOPIC_NAME)

        with sender:
            message = {
                "url": url,
                "text": text
            }

            sb_message = ServiceBusMessage(json.dumps(message))

            sender.send_messages(sb_message)