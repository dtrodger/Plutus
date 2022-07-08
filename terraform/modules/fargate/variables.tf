variable "ecs_task_cpu" {
    description = "ECS task cpu allocated"
    type        = number
    default     = 4096
}

variable "ecs_task_memory" {
    description = "ECS task memory allocated"
    type        = number
    default     = 8192
}

variable "project_version" {
    description = "Version"
    type = string
}

variable "env" {
    description = "Enviornment"
    type = string
}

variable "exchange" {
    description = "Exchange"
    type = string
}

variable "rds_port" {
    description = "RDS port"
    type = string
}

variable "rds_host" {
    description = "RDS host"
    type = string
}

variable "rds_user" {
    description = "RDS user"
    type = string
}

variable "rds_password" {
    description = "RDS password"
    type = string
}

variable "log_level" {
    description = "Log level"
    type = string
}