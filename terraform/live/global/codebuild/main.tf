terraform {
    required_version = "~> 1.0"

    backend "s3" {
        bucket = "airstudio-terraform-state-backend"
        key = "plutus/global/codebuild/terraform.tfstate"
        region = "us-west-1"
        dynamodb_table = "terraform_state"
        encrypt = true
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

locals {
    tags = {
        "DeployedBy" = "terraform"
        "Service" = "codebuild"
    }
}

resource "aws_s3_bucket" "dist" {
  bucket = "airstudio-dist"
  acl    = "private"
  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        sse_algorithm     = "AES256"
      }
    }
  }
  tags = local.tags
}

data "aws_iam_policy_document" "codebuild_role_assume_policy_doc" {
    statement {
        actions = ["sts:AssumeRole"]
        effect = "Allow"

        principals {
            type = "Service"
            identifiers = ["codebuild.amazonaws.com"]
        }
    }
}

resource "aws_iam_role" "codebuild_iam_role" {
    name = "parser_pipeline_codebuild_role"
    assume_role_policy = data.aws_iam_policy_document.codebuild_role_assume_policy_doc.json
}

resource "aws_iam_role_policy" "codebuild_role_policy" {
    name = "codebuild-role-policy"
    role = aws_iam_role.codebuild_iam_role.name

    policy = jsonencode({
        Version = "2012-10-17"
        Statement = [
            {
                Effect = "Allow"
                Action = "*"
                Resource = "*"
            }
        ]
    })
}

resource "aws_cloudwatch_log_group" "airstudio_api_ci" {
    name = "codebuild/airstudio-api/ci"
    tags = local.tags
}

resource "aws_codebuild_project" "airstudio_api_ci" {
    name = "airstudio-api-ci"
    description = "Codebuild project to run Airstudio API's tests"
    build_timeout = 60
    queued_timeout = 120
    service_role = aws_iam_role.codebuild_iam_role.arn

    artifacts {
        type = "NO_ARTIFACTS"
    }

    environment {
        compute_type = "BUILD_GENERAL1_SMALL"
        image_pull_credentials_type = "CODEBUILD"
        image = "aws/codebuild/amazonlinux2-x86_64-standard:3.0"
        privileged_mode = true
        type = "LINUX_CONTAINER"

        environment_variable {
            name = "S3_BUCKET_NAME"
            value = aws_s3_bucket.dist.id
        }
    }

    logs_config {
        cloudwatch_logs {
            group_name = aws_cloudwatch_log_group.airstudio_api_ci.name
            status = "ENABLED"
        }
    }

    source {
        type = "CODECOMMIT"
        location = "https://git-codecommit.us-west-1.amazonaws.com/v1/repos/airstudio-api"
        buildspec = "codebuild/ci-buildspec.yml"
    }

    source_version = "main"
    tags = local.tags
}

resource "aws_cloudwatch_log_group" "airstudio_api_cd" {
    name = "codebuild/airstudio-api/cd"
    tags = local.tags
}

resource "aws_codebuild_project" "airstudio_api_cd" {
    name = "airstudio-api-cd"
    description = "Codebuild project to run Airstudio API's deployment job"
    build_timeout = 60
    queued_timeout = 120
    service_role = aws_iam_role.codebuild_iam_role.arn

    artifacts {
        type = "NO_ARTIFACTS"
    }

    environment {
        compute_type = "BUILD_GENERAL1_SMALL"
        image_pull_credentials_type = "CODEBUILD"
        image = "aws/codebuild/amazonlinux2-x86_64-standard:3.0"
        privileged_mode = true
        type = "LINUX_CONTAINER"

        environment_variable {
            name = "S3_BUCKET_NAME"
            value = aws_s3_bucket.dist.id
        }
    }

    logs_config {
        cloudwatch_logs {
            group_name = aws_cloudwatch_log_group.airstudio_api_cd.name
            status = "ENABLED"
        }
    }

    source {
        type = "CODECOMMIT"
        location = "https://git-codecommit.us-west-1.amazonaws.com/v1/repos/airstudio-api"
        buildspec = "codebuild/cd-buildspec.yml"
    }

    source_version = "main"
}

resource "aws_cloudwatch_log_group" "airstudio_ui_ci" {
    name = "codebuild/airstudio-ui/ci"
    tags = local.tags
}

resource "aws_codebuild_project" "airstudio_ui_ci" {
    name = "airstudio-ui-ci"
    description = "Codebuild project to run Airstudio UI's tests"
    build_timeout = 60
    queued_timeout = 120
    service_role = aws_iam_role.codebuild_iam_role.arn

    artifacts {
        type = "NO_ARTIFACTS"
    }

    environment {
        compute_type = "BUILD_GENERAL1_SMALL"
        image_pull_credentials_type = "CODEBUILD"
        image = "aws/codebuild/amazonlinux2-x86_64-standard:3.0"
        privileged_mode = true
        type = "LINUX_CONTAINER"

        environment_variable {
            name = "S3_BUCKET_NAME"
            value = aws_s3_bucket.dist.id
        }
    }

    logs_config {
        cloudwatch_logs {
            group_name = aws_cloudwatch_log_group.airstudio_ui_ci.name
            status = "ENABLED"
        }
    }

    source {
        type = "CODECOMMIT"
        location = "https://git-codecommit.us-west-1.amazonaws.com/v1/repos/airstudio-ui"
        buildspec = "codebuild/ci-buildspec.yml"
    }

    source_version = "main"
    tags = local.tags
}

resource "aws_cloudwatch_log_group" "airstudio_ui_cd" {
    name = "codebuild/airstudio-ui/cd"
    tags = local.tags
}

resource "aws_codebuild_project" "airstudio_ui_cd" {
    name = "airstudio-ui-cd"
    description = "Codebuild project to run Airstudio UI's deployment job"
    build_timeout = 60
    queued_timeout = 120
    service_role = aws_iam_role.codebuild_iam_role.arn

    artifacts {
        type = "NO_ARTIFACTS"
    }

    environment {
        compute_type = "BUILD_GENERAL1_SMALL"
        image_pull_credentials_type = "CODEBUILD"
        image = "aws/codebuild/amazonlinux2-x86_64-standard:3.0"
        privileged_mode = true
        type = "LINUX_CONTAINER"

        environment_variable {
            name = "S3_BUCKET_NAME"
            value = aws_s3_bucket.dist.id
        }
    }

    logs_config {
        cloudwatch_logs {
            group_name = aws_cloudwatch_log_group.airstudio_ui_cd.name
            status = "ENABLED"
        }
    }

    source {
        type = "CODECOMMIT"
        location = "https://git-codecommit.us-west-1.amazonaws.com/v1/repos/airstudio-ui"
        buildspec = "codebuild/cd-buildspec.yml"
    }

    source_version = "main"
}