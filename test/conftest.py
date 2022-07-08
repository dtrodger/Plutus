"""
Test fixtures
"""

import moto
import pytest
import boto3

from plutus import util
from plutus.db import util as db_util


@pytest.fixture(scope="session", autouse=True)
def clean_db():
    """
    Truncates the SQL database when tests complete
    """

    db_util.truncate_sql_db()
    if "prod" in util.get_env_var("SQL_HOST"):
        raise Exception("Cannot truncate production database")
    yield
    db_util.truncate_sql_db()


@pytest.fixture(scope="session")
def sql_session():
    """
    SQL session
    """

    return db_util.get_sql_session()


@pytest.fixture()
def sqs():
    """
    AWS SQS client
    """

    with moto.mock_sqs():
        yield boto3.client("sqs")


@pytest.fixture()
def sqs_ticker_queue(sqs):
    """
    AWS SQS ticker queue
    """

    queue = sqs.create_queue(QueueName="ticker")
    util.set_env_var("SQS_TICKER_QUEUE_URL", queue["QueueUrl"])
    return queue
