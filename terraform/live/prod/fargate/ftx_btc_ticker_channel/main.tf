terraform {
    required_version = "~> 1.0"
    backend "s3" {
        key = "plutus/prod/fargate/ftx_btc_ticker_channel/terraform.tfstate"
    }
    required_providers {
        aws = {
            source = "hashicorp/aws"
            version = "~> 3.0"
        }
    }
}

provider "aws" {
    region = "us-west-1"
}

data "terraform_remote_state" "sqs" {
    backend = "s3"

    config = {
        bucket = var.remote_state_bucket
        key = "plutus/prod/sqs/terraform.tfstate"
        region = var.region
    }
}

module "sqs" {
    source = "../../../../modules/fargate"
    env = var.env
    ecs_task_cpu = var.ecs_task_cpu
    ecs_task_memory = var.ecs_task_memory
    project_version = var.project_version
    exchange = var.exchange
    symbol = var.symbol
    sqs_ticker_queue_url = data.terraform_remote_state.sqs.outputs.plutus_queue_url
}
