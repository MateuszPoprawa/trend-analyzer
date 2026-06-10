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
OUTPUT_TOPIC = "summary-results"

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
        url = data.get("url")
        text = data.get("text", "")
        
        logging.info("Url: " + url)
        logging.info("Text: " + text)

        client = get_ai_client()

        poller = client.begin_abstract_summary([text])
        summary = poller.result()
        
        logging.info("Summary generated")

        send_to_service_bus(url, summary)

    except Exception as e:
        logging.error(str(e))


# =========================
# SERVICE BUS OUTPUT
# =========================
def send_to_service_bus(url: str, summary: str):

    client = ServiceBusClient.from_connection_string(
        conn_str=SERVICE_BUS_CONN
    )

    with client:
        sender = client.get_topic_sender(topic_name=OUTPUT_TOPIC)

        with sender:
            message = {
                "url": url,
                "summary": summary
            }

            sender.send_messages(
                ServiceBusMessage(json.dumps(message))
            )