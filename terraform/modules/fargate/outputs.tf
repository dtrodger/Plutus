output "fargate_task_security_group_id" {
    value = aws_security_group.ecs_security_group.id
}

output "fargate_task_arn" {
    value = aws_ecs_task_definition.task.arn
}
