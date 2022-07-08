locals {
    tags = {
        DeployedBy="terraform"
        Service="Plutus"
    }
}

resource "aws_sqs_queue" "ticker_dlq" {
  name = "ticker-dlq"
  tags = local.tags
}

resource "aws_sqs_queue" "ticker_queue" {
    name = "ticker"
    visibility_timeout_seconds = 90
    redrive_policy = jsonencode({
        deadLetterTargetArn = aws_sqs_queue.ticker_dlq.arn
        maxReceiveCount = 1
    })
    tags = local.tags
}
