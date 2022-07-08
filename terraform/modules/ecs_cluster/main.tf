locals {
    tags = {
        DeployedBy="terraform"
        Service="Plutus"
    }
}

resource "aws_cloudwatch_log_group" "ecs_cluster_logs" {
  name              = "${var.env}-plutus-cluster"
  retention_in_days = 90
  tags              = local.tags
}

resource "aws_kms_key" "ecs_cluster_key" {
  description             = "${var.env}-plutus-esc-cluster-key"
  deletion_window_in_days = 7
}

resource "aws_ecs_cluster" "cluster" {
  name = "${var.env}-plutus-cluster"
  capacity_providers = ["FARGATE"]

  configuration {
    execute_command_configuration {
      kms_key_id = aws_kms_key.ecs_cluster_key.arn
      logging    = "OVERRIDE"
      log_configuration {
        cloud_watch_encryption_enabled = true
        cloud_watch_log_group_name     = aws_cloudwatch_log_group.ecs_cluster_logs.name
      }
    }
  }

  setting {
    name = "containerInsights"
    value = "enabled"
  }

  tags = local.tags
}
