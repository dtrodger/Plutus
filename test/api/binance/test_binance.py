"""
Binance API tests
"""

import asyncio

from plutus.api import binance


def test_process_ticker_channel_event(
    sqs, sqs_ticker_queue, binance_ticker_channel_message
):
    """
    Test processing a Binance price channel event
    """

    asyncio.run(
        binance.process_ticker_channel_event(sqs, "btc", binance_ticker_channel_message)
    )
