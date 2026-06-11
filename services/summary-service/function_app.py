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

COSMOS_URI = os.environ["COSMOS_URI"]
COSMOS_KEY = os.environ["COSMOS_KEY"]
DB_NAME = "summarydb"
CONTAINER_NAME = "summaries"

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
    topic_name="summary-results",
    subscription_name="summary-subscription",
    connection="SERVICE_BUS_CONNECTION"
)
def summary_service(msg: func.ServiceBusMessage):

    logging.info("Summary Service triggered")

    data = json.loads(msg.get_body().decode("utf-8"))

    id = data["id"]
    url = data["url"]
    summary = data["summary"]
    
    summary_result = {
        "id": id,
        "url": url,
        "summary": summary
    }

    # =========================
    # SAVE TO COSMOS DB
    # =========================
    container.upsert_item(summary_result)

# =========================
# HTTP Endpoint
# =========================

@app.route(
    route="summaries",
    methods=["GET"],
    auth_level=func.AuthLevel.ANONYMOUS
)
def get_summary(req: func.HttpRequest):

    id = req.params.get("id")
    url = req.params.get("url")

    if not id:
        return func.HttpResponse(
            "Missing id parameter",
            status_code=400
        )

    try:
        logging.info("ID: " + id)
        item = container.read_item(item=id, partition_key=url)

        return func.HttpResponse(
            body=json.dumps(item),
            mimetype="application/json",
            status_code=200
        )

    except Exception as e:
        logging.info(e)
        return func.HttpResponse(
            body=json.dumps({
                "status": "processing"
            }),
            mimetype="application/json",
            status_code=404
        )