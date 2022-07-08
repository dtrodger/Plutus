locals {
    tags = {
        DeployedBy="terraform"
        Service="Plutus"
    }
    task_id = "${var.env}-${var.exchange}-${var.symbol}"
}

data "terraform_remote_state" "vpc" {
    backend = "s3"
    config = {
        bucket = "airstudio-terraform-state-backend"
        key = "vpc/terraform.tfstate"
        region = "us-east-2"
    }
}

resource "aws_iam_role" "ecs_task_execution_role" {
  name = "${local.task_id}-fargate-task-execution"
  assume_role_policy = jsonencode(
    {
      "Version": "2012-10-17",
      "Statement": [
        {
          "Action": "sts:AssumeRole",
          "Principal": {
            "Service": "ecs-tasks.amazonaws.com"
          },
          "Effect": "Allow",
          "Sid": ""
        }
      ]
    }
  )
  tags = local.tags
}

resource "aws_iam_role" "ecs_task_role" {
  name = "${local.task_id}-fargate-task"
  assume_role_policy = jsonencode(
    {
      "Version": "2012-10-17",
      "Statement": [
        {
          "Action": "sts:AssumeRole",
          "Principal": {
            "Service": "ecs-tasks.amazonaws.com"
          },
          "Effect": "Allow",
          "Sid": ""
        }
      ]
    }
  )
  tags = local.tags
}

resource "aws_iam_role_policy_attachment" "ecs_task_execution_role_policy" {
  role       = aws_iam_role.ecs_task_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

resource "aws_cloudwatch_log_group" "ecs_task_logs" {
  name              = "${local.task_id}-task"
  retention_in_days = 90
  tags              = local.tags
}

resource "aws_ecs_task_definition" "task" {
  family                   = var.task
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = var.ecs_task_cpu
  memory                   = var.ecs_task_memory
  task_role_arn            = aws_iam_role.ecs_task_role.arn
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn

  runtime_platform {
    operating_system_family = "LINUX"
    cpu_architecture        = "X86_64"
  }

  container_definitions    = jsonencode(
    [
      {
        "name": "${local.task_id}-ticker-channel",
        "image": "642030467107.dkr.ecr.us-west-1.amazonaws.com/plutus:${var.version}",
        "cpu": var.ecs_task_cpu,
        "memory": var.ecs_task_memory,
        "command": ["python", "plutus/cli.py", "process-price-feed", var.exchange, var.symbol],
        "environment": [
            {
                "name": "ENVIRONMENT",
                "value": var.env
            },
            {
                "name": "SQS_TICKER_QUEUE_URL",
                "value": var.sqs_ticker_queue_url
            },
            {
                "name": "LOG_LEVEL",
                "value": var.log_level
            },
        ],
        "logConfiguration": {
          "logDriver": "awslogs",
          "options": {
            "awslogs-group": aws_cloudwatch_log_group.ecs_task_logs.name,
            "awslogs-region": "us-east-2",
            "awslogs-stream-prefix": "create-product-variants"
          }
        }
      }
    ]
  )
  tags = local.tags
}

resource "aws_security_group" "fargate_security_group" {
  name        = "${local.task_id}-sg"
  description = "Security group for the ${local.task_id} ECS task"
  vpc_id      = data.terraform_remote_state.vpc.outputs.vpc_id
  tags        = local.tags
}

resource "aws_security_group_rule" "ingress" {
    type = "ingress"
    description = "Allows PostgreSQL connection"
    from_port         = 0
    to_port           = 0
    protocol          = "-1"
    cidr_blocks       = ["0.0.0.0/0"]
    security_group_id = aws_security_group.fargate_security_group.id
}

resource "aws_security_group_rule" "egress" {
    type              = "egress"
    description       = "Allow ECS task to connect to anything"
    from_port         = 0
    to_port           = 0
    protocol          = "-1"
    cidr_blocks       = ["0.0.0.0/0"]
    security_group_id = aws_security_group.fargate_security_group.id
}
