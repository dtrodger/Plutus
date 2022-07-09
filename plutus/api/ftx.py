"""
FTX API
"""

import json
import datetime

from websockets import connect

from plutus.api import aws


FTX_WEBSOCKET_ENDPOINT = "wss://ftx.com/ws/"
SYMBOL_TO_CHANNEL = {"btc": "BTC-PERP"}


async def process_ticker_channel(symbol):
    """
    Processes the FTX ticker websocket channel
    """

    sqs = aws.sqs_client()
    async with connect(f"{FTX_WEBSOCKET_ENDPOINT}") as ws:
        await ws.send(
            ticker_channel_subscription_request(SYMBOL_TO_CHANNEL.get(symbol))
        )
        while True:
            raw_event = await ws.recv()
            await process_ticker_channel_event(sqs, symbol, raw_event)


async def process_ticker_channel_event(sqs, symbol, raw_event):
    """
    Sends a FTX price channel event to SQS
    """

    event = json.loads(raw_event)
    if event.get("data"):
        event_data = event["data"]
        event_time = datetime.datetime.utcfromtimestamp(event_data["time"]).strftime(
            "%Y-%m-%d-%H-%M-%S"
        )
        event["instant"] = event_time
        event["symbol"] = symbol
        event["exchange"] = "ftx"
        aws.send_sqs_price_queue_message(sqs, event)


def ticker_channel_subscription_request(symbol):
    """
    Gets a ticker channel subscription request
    """

    return json.dumps({"op": "subscribe", "channel": "ticker", "market": symbol})


def sql_price_fields_from_sqs_message(sqs_message):
    """
    Gets SQL Price fields from an SQS message
    """

    return {
        "instant": datetime.datetime.strptime(
            sqs_message["instant"], "%Y-%m-%d-%H-%M-%S"
        ),
        "exchange": sqs_message["exchange"],
        "symbol": sqs_message["symbol"],
        "bid": sqs_message["data"]["bid"],
        "ask": sqs_message["data"]["ask"],
        "price": sqs_message["data"]["last"],
    }
