"""
Binance API
"""

import json
import datetime

from websockets import connect

from plutus.api import aws


BINANCE_WEBSOCKET_ENDPOINT = "wss://stream.binance.com:9443/ws/"
ENV_SYMBOL_TO_CHANNEL = {"btc": "btcusdc@ticker"}


async def process_ticker_channel(symbol):
    """
    Processes the Binance pricing channel
    """

    sqs = aws.sqs_client()
    pong_time = datetime.datetime.utcnow()
    async with connect(
        f"{BINANCE_WEBSOCKET_ENDPOINT}{ENV_SYMBOL_TO_CHANNEL.get(symbol)}"
    ) as ws:
        while True:
            seconds_since_pong = (datetime.datetime.utcnow() - pong_time).total_seconds()
            if seconds_since_pong > (60 * 3):
                await ws.pong()

            raw_event = await ws.recv()
            await process_ticker_channel_event(sqs, symbol, raw_event)


async def process_ticker_channel_event(sqs, symbol, raw_event):
    """
    Sends a Binance price channel event to SQS
    """

    event = json.loads(raw_event)
    if event.get("E"):
        event_time = datetime.datetime.utcfromtimestamp(event["E"] / 1000).strftime(
            "%Y-%m-%d-%H-%M-%S"
        )
        event["instant"] = event_time
        event["symbol"] = symbol
        event["exchange"] = "binance"
        aws.send_sqs_price_queue_message(sqs, event)


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
        "bid": sqs_message["b"],
        "ask": sqs_message["a"],
        "price": sqs_message["c"],
    }
