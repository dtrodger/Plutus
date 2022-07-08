"""
Websocket channel utils
"""

import time
import datetime
import json

from websockets import connect

from plutus import util
from plutus.db import model
from plutus.db import util as db_util
from plutus.api import ftx, binance


async def process_ticker_channels():
    """
    Processes the FTX and Binance price feeds
    """

    redis = util.redis_client()
    async with connect(
        f"{binance.BINANCE_ENDPOINT}{binance.BINANCE_BITCOIN_STREAM}"
    ) as binance_ws, connect(ftx.FTX_ENDPOINT) as ftx_ws:
        await ftx_ws.send(ftx.price_channel_subscription_request("BTC-PERP"))
        while True:
            await ftx.process_ticker_channel(ftx_ws, redis)
            await binance.process_ticker_channel(binance_ws, redis)
            time.sleep(1)


async def price_cache_sql_etl():
    """
    ETLs pricing data from Redis into SQL
    """

    sql_session = db_util.get_sql_session()
    redis = util.redis_client()
    today = datetime.datetime.utcnow()
    current_second = today.replace(hour=0, minute=0, second=0)
    end_second = today.replace(hour=23, minute=59, second=59)
    prices = []
    while current_second <= end_second:
        current_second_str = current_second.strftime("%m-%d-%Y-%H-%M-%S")
        cache_record = await redis.get(f"{current_second_str}-btc")
        if cache_record:
            cache_record = json.loads(cache_record)
            ftx_price = cache_record.get("ftx", {})
            binance_price = cache_record.get("binance", {})
            price = model.Price.insert(
                sql_session,
                instant=current_second,
                symbol=cache_record["sybmol"],
                binance_bid=binance_price.get("bid"),
                binance_ask=binance_price.get("ask"),
                binance_price=binance_price.get("price"),
                ftx_bid=ftx_price.get("bid"),
                ftx_ask=ftx_price.get("ask"),
                ftx_price=ftx_price.get("price"),
            )
            prices.append(price)

        current_second += datetime.timedelta(seconds=1)

    sql_session.bulk_save_objects(prices)
