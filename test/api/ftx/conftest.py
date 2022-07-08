"""
FTX API fixtures
"""

import json

import pytest


@pytest.fixture
def ftx_ticker_channel_message():
    """
    FTX ticker channel message
    """

    return json.dumps(
        {
            "channel": "ticker",
            "market": "BTC-PERP",
            "type": "update",
            "data": {
                "bid": 21878.0,
                "ask": 21879.0,
                "bidSize": 2.3795,
                "askSize": 3.9966,
                "last": 21883.0,
                "time": 1657312676.3783073,
            },
        }
    )
