"""
AWS Lambda SQS ticket queue fixtures
"""

import json

import pytest


@pytest.fixture()
def sqs_ticker_queue_binance_message(sqs, sqs_ticker_queue):
    """
    SQS Binance ticker queue message
    """

    return sqs.send_message(
        QueueUrl=sqs_ticker_queue["QueueUrl"],
        MessageBody=json.dumps(
            {
                "e": "24hrTicker",
                "E": 1657302537180,
                "s": "BTCUSDC",
                "p": "860.73000000",
                "P": "4.121",
                "w": "21673.04424007",
                "x": "20888.97000000",
                "c": "21746.85000000",
                "Q": "0.00161000",
                "b": "21742.67000000",
                "B": "0.13500000",
                "a": "21743.78000000",
                "A": "0.00260000",
                "o": "20886.12000000",
                "h": "22500.00000000",
                "l": "20869.16000000",
                "v": "8140.04960000",
                "q": "176419655.09716130",
                "O": 1657216137172,
                "C": 1657302537172,
                "F": 47486462,
                "L": 47636827,
                "n": 150366,
                "instant": "2022-07-08-17-48-57",
                "symbol": "btc",
                "exchange": "binance",
            }
        ),
    )


@pytest.fixture()
def sqs_ticker_queue_ftx_message(sqs, sqs_ticker_queue):
    """
    SQS FTX ticker queue message
    """

    return sqs.send_message(
        QueueUrl=sqs_ticker_queue["QueueUrl"],
        MessageBody=json.dumps(
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
                "instant": "2022-07-08-20-37-56",
                "symbol": "btc",
                "exchange": "ftx",
            }
        ),
    )


@pytest.fixture()
def sqs_ticker_queue_binance_message_reception(
    sqs, sqs_ticker_queue, sqs_ticker_queue_binance_message
):
    """
    SQS FTX ticker queue message reception
    """

    return sqs.receive_message(
        QueueUrl=sqs_ticker_queue["QueueUrl"],
    )


@pytest.fixture()
def sqs_ticker_queue_ftx_message_reception(
    sqs, sqs_ticker_queue, sqs_ticker_queue_ftx_message
):
    """
    SQS Binance ticker queue message reception
    """

    return sqs.receive_message(
        QueueUrl=sqs_ticker_queue["QueueUrl"],
    )


@pytest.fixture()
def ticker_queue_ftx_message_lambda_event(sqs_ticker_queue_ftx_message_reception):
    """
    AWS SQS ticker queue FTX message event
    """

    sqs_message = sqs_ticker_queue_ftx_message_reception["Messages"][0]
    return {
        "Records": [
            {
                "messageId": sqs_message["MessageId"],
                "receiptHandle": sqs_message["ReceiptHandle"],
                "body": sqs_message["Body"],
            }
        ]
    }


@pytest.fixture()
def ticker_queue_binance_message_lambda_event(
    sqs_ticker_queue_binance_message_reception,
):
    """
    AWS SQS ticker queue Binance message event
    """

    sqs_message = sqs_ticker_queue_binance_message_reception["Messages"][0]
    return {
        "Records": [
            {
                "messageId": sqs_message["MessageId"],
                "receiptHandle": sqs_message["ReceiptHandle"],
                "body": sqs_message["Body"],
            }
        ]
    }
