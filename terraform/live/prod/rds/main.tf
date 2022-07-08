terraform {
    required_version = "~> 1.0"
    backend "s3" {
        key = "plutus/prod/rds/terraform.tfstate"
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

module "sqs" {
    source = "../../../modules/rds"
    env = var.env
}
