"""
FTX API tests
"""

import asyncio

from plutus.api import ftx


def test_process_ticker_channel_event(
    sqs, sqs_ticker_queue, ftx_ticker_channel_message
):
    """
    Test processing a Binance price channel event
    """

    asyncio.run(
        ftx.process_ticker_channel_event(sqs, "btc", ftx_ticker_channel_message)
    )
