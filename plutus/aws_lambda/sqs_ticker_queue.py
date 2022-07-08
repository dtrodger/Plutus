"""
AWS Lambda SQS ticker queue handler
"""

import logging
import json

from plutus import util
from plutus.db import util as db_util
from plutus.db import model
from plutus.api import (
    ftx, binance
)


log = logging.getLogger(__name__)


def handler(event, context):
    """
    AWS Lambda SQS ticker queue handler
    """

    util.configure_logging()
    sql_session = db_util.get_sql_session()
    for sqs_message in event["Records"]:
        try:
            sql_fields = sql_fields_from_sqs_message(sqs_message["body"])
            if not model.Price.get(
                sql_session,
                symbol=sql_fields["symbol"],
                exchange=sql_fields["exchange"],
                instant=sql_fields["instant"],
            ):
                price = model.Price.insert(
                    sql_session,
                    **sql_fields
                )
                log.info(f"Added {price}")
        except Exception as e:
            log.error(f"Failed to process message {sqs_message} with {e}")


def sql_fields_from_sqs_message(sqs_message):
    """
    Gets the required Price model fields from an SQS message
    """
    sqs_message = json.loads(sqs_message)

    return {
        "binance": binance.sql_price_fields_from_sqs_message,
        "ftx": ftx.sql_price_fields_from_sqs_message
    }[sqs_message["exchange"]](sqs_message)
