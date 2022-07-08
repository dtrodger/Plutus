output "plutus_queue_arn" {
    value = aws_sqs_queue.plutus_queue.arn
}

output "plutus_queue_url" {
    value = aws_sqs_queue.plutus_queue.url
}
