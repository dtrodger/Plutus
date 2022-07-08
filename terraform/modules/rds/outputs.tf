output "rds_host" {
    value = aws_db_instance.plutus.address
}

output "rds_id" {
    value = aws_db_instance.plutus.id
}

output "rds_port" {
    value = aws_db_instance.plutus.port
}

output "rds_security_group_id" {
    value = aws_security_group.plutus.id
}
