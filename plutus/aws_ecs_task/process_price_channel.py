"""
AWS ECS processes price channel handler
"""

import logging
import asyncio

from plutus import util
from plutus.api import ftx, binance


log = logging.getLogger(__name__)


async def handler(exchange, symbol):
    """
    AWS ECS processes price channel handler
    """

    util.configure_logging()
    ticker_channel_handlers = {
        "binance": binance.process_ticker_channel,
        "ftx": ftx.process_ticker_channel,
    }
    while True:
        try:
            await ticker_channel_handlers[exchange](symbol)
        except Exception as e:
            log.error(e)


if __name__ == "__main__":
    """
    Task entrypoint
    """

    exchange = util.get_env_var("EXCHANGE")
    symbol = util.get_env_var("SYMBOL")
    asyncio.run(handler(exchange, symbol))
