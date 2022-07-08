locals {
    psql_port     = 5432
    all_ports      = 0
    tcp_protocol   = "tcp"
    all_protocols  = "-1"
    all_ip_address = "0.0.0.0/0"
    rds_identifier = "${var.env}-plutus-db"
}

data "terraform_remote_state" "vpc" {
    backend = "s3"
    config = {
        bucket = "airstudio-terraform-state-backend"
        key = "vpc/terraform.tfstate"
        region = "us-east-2"
    }
}

resource "aws_security_group" "plutus" {
    name = "${local.rds_identifier}-connections"
    description = "Allow connections to rds instance ${local.rds_identifier}"
    vpc_id = data.terraform_remote_state.vpc.outputs.vpc_id
}

resource "aws_security_group_rule" "ingress_rule_cidr" {
    type = "ingress"
    description = "Connect to ${local.rds_identifier} rds instance"
    from_port         = local.psql_port
    to_port           = local.psql_port
    protocol          = "-1"
    cidr_blocks       = ["0.0.0.0/0"]
    security_group_id = aws_security_group.plutus.id
}

resource "aws_security_group_rule" "egress_rule" {
    type = "egress"
    from_port = local.all_ports
    to_port = local.all_ports
    protocol = local.all_protocols
    cidr_blocks = [local.all_ip_address]
    security_group_id = aws_security_group.plutus.id
}

resource "aws_db_instance" "plutus" {
  allocated_storage    = 10
  engine               = "postgres"
  engine_version       = "12.7"
  instance_class       = "db.t2.micro"
  name                 = "plutus"
  username             = "postgres"
  password             = "admin"
  vpc_security_group_ids = [aws_security_group.plutus.id]
  skip_final_snapshot  = true
}
