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

variable "version" {
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

variable "symbol" {
    description = "Symbol"
    type = string
}

variable "log_level" {
    description = "Log level"
    type = string
}