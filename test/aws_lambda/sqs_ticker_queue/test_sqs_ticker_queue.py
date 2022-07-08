"""
Test AWS Lambda SQS ticker queue
"""

from plutus.aws_lambda import sqs_ticker_queue


def test_binance_ticker_message_reception(ticker_queue_binance_message_lambda_event):
    """
    Test Lambda reception of a Binance ticker SQS message
    """

    sqs_ticker_queue.handler(ticker_queue_binance_message_lambda_event, {})


def test_ftx_ticker_message_reception(ticker_queue_ftx_message_lambda_event):
    """
    Test Lambda reception of a FTX ticker SQS message
    """

    sqs_ticker_queue.handler(ticker_queue_ftx_message_lambda_event, {})
