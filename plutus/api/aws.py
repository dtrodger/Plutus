"""
AWS API
"""

import uuid
import json

import boto3

from plutus import util


def aws_client(service: str):
    """
    Gets an AWS service client
    """

    if util.get_env_var("ENVIRONMENT") == "local":
        client = boto3.client(
            service,
            region_name="us-east-2",
            aws_access_key_id=util.get_env_var("AWS_ACCESS_KEY"),
            aws_secret_access_key=util.get_env_var("AWS_SECRET_ACCESS_KEY"),
        )
    else:
        client = boto3.client(service, region_name="us-east-2")

    return client


def aws_resource(resource: str):
    """
    Gets an AWS resource
    """

    if util.get_env_var("ENVIRONMENT") == "local":
        resource = boto3.resource(
            resource,
            region_name="us-east-2",
            aws_access_key_id=util.get_env_var("AWS_ACCESS_KEY"),
            aws_secret_access_key=util.get_env_var("AWS_SECRET_ACCESS_KEY"),
        )
    else:
        resource = boto3.resource(resource, region_name="us-east-2")

    return resource


def aws_session():
    """
    Gets an AWS session
    """

    if util.get_env_var("ENVIRONMENT") == "local":
        session = boto3.Session(
            aws_access_key_id=util.get_env_var("AWS_ACCESS_KEY"),
            aws_secret_access_key=util.get_env_var("AWS_SECRET_ACCESS_KEY"),
        )
    else:
        session = boto3.Session()

    return session


def sqs_client():
    """
    Gets an AWS SQS client
    """

    return aws_client("sqs")


def send_sqs_message(sqs, queue_url, message):
    """
    Sends a message to an SQS queue
    """

    sqs.send_message(
        QueueUrl=queue_url,
        MessageBody=json.dumps(
            {
                "Id": str(uuid.uuid4()),
                "MessageBody": message,
            }
        ),
    )


def send_sqs_price_queue_message(sqs, message):
    """
    Sends a message to the SQS price queue
    """

    send_sqs_message(sqs, util.get_env_var("SQS_PRICE_QUEUE_URL"), message)
