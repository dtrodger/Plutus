#!/usr/bin/env python

import time
import hmac
import json
import asyncio
import time
import datetime

from websockets import connect
from requests import Request

BINANCE_BITCOIN_STREAM = "btcusdc@ticker"
BINANCE_ENDPOINT = "wss://stream.binance.com:9443/ws/"

FTX_ENDPOINT = "wss://ftx.com/ws/"
FTX_API_KEY = "uOMPUqEK7u3UJH8EFY4pLIOb2USHIaKFVgYn7UQ6"
FTX_API_SECRET = "dFPO1kEDA2SkeuK6ikYEjamRg_1D46NyGbrA5vtS"

REDIS_CONNECTION = "redis://localhost"


def ftx_signed_key():
    """
    Gets an FTX signed API key
    """

    request = Request("GET", "wss://ftx.com/ws/")
    prepared = request.prepare()
    signature_payload = (
        f"{int(time.time() * 1000)}{prepared.method}{prepared.path_url}".encode()
    )
    signature = hmac.new(
        FTX_API_SECRET.encode(), signature_payload, "sha256"
    ).hexdigest()

    return signature


async def main():
    redis = aioredis.from_url(REDIS_CONNECTION)
    s = ftx_signed_key()
    async with connect(
        f"{BINANCE_ENDPOINT}{BINANCE_BITCOIN_STREAM}"
    ) as binance_ws, connect(FTX_ENDPOINT) as ftx_ws:
        await ftx_ws.send(
            json.dumps({"op": "subscribe", "channel": "ticker", "market": "BTC-PERP"})
        )
        while True:
            ftx_raw_event = await ftx_ws.recv()
            ftx_event = json.loads(ftx_raw_event)
            if ftx_event.get("data"):
                event_time = datetime.datetime.fromtimestamp(
                    ftx_event["data"]["time"] / 1000
                ).strftime("%m-%d-%Y-%H-%M-%S")
                print(ftx_event)

            time.sleep(0.1)

        # await binance_ws.send(json.dumps({
        #     "method": "SUBSCRIBE",
        #     "params":[
        #         BINANCE_BITCOIN_STREAM
        #     ],
        #     "id": 1
        # }))
        # while True:
        #     raw_event = await binance_ws.recv()
        #     event = json.loads(raw_event)
        #     if event.get("E"):
        #         event_time = datetime.datetime.fromtimestamp(event["E"] / 1000).strftime("%m-%d-%Y-%H-%M-%S")
        #         record_key = f"{event_time}-btcusdc"
        #         record = await redis.get(record_key)
        #         if not record:
        #             record = json.dumps({
        #                 "sybmol": "btcusdc",
        #                 "binance": event["c"]
        #             })
        #             await redis.set(record_key, record)
        #         else:
        #             record = json.loads(record)
        #             record["binance"] = event["c"]
        #             record = json.dumps(record)
        #             await redis.set(record_key, record)

        #         time.sleep(0.1)


asyncio.run(main())
