# Firm Ecosystem — Terraform Module
#
# Deploys MCP server and optional Memory server to AWS ECS Fargate.
#
# Usage:
#   module "firm" {
#     source       = "./deploy/terraform"
#     region       = "eu-west-1"
#     firm_version = "3.3.0"
#   }
#
# ⚠️ Contenu généré par IA — validation humaine requise avant utilisation.

terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 5.0"
    }
  }
}

# ── Variables ────────────────────────────────────────────────────────────────

variable "provider_name" {
  description = "Cloud provider (currently only aws is implemented)"
  type        = string
  default     = "aws"

  validation {
    condition     = contains(["aws"], var.provider_name)
    error_message = "Currently only 'aws' is supported."
  }
}

variable "region" {
  description = "AWS region for deployment"
  type        = string
  default     = "us-east-1"
}

variable "firm_version" {
  description = "Docker image version tag"
  type        = string
  default     = "3.3.0"
}

variable "mcp_port" {
  description = "MCP server port"
  type        = number
  default     = 8012
}

variable "memory_port" {
  description = "Memory server port"
  type        = number
  default     = 8765
}

variable "enable_memory_server" {
  description = "Deploy memory server alongside MCP server"
  type        = bool
  default     = true
}

variable "cpu" {
  description = "CPU units for ECS task (256, 512, 1024, 2048)"
  type        = number
  default     = 512
}

variable "memory" {
  description = "Memory in MB for ECS task"
  type        = number
  default     = 1024
}

variable "environment" {
  description = "Extra environment variables for the containers"
  type        = map(string)
  default     = {}
}

variable "name_prefix" {
  description = "Prefix for all created resources"
  type        = string
  default     = "firm"
}

# ── Provider ─────────────────────────────────────────────────────────────────

provider "aws" {
  region = var.region
}

# ── Data ─────────────────────────────────────────────────────────────────────

data "aws_vpc" "default" {
  default = true
}

data "aws_subnets" "default" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
}

# ── ECR / Image ──────────────────────────────────────────────────────────────

locals {
  mcp_image    = "ghcr.io/romainsantoli-web/mcp-openclaw-extensions:${var.firm_version}"
  memory_image = "ghcr.io/romainsantoli-web/memory-os-ai:${var.firm_version}"
}

# ── ECS Cluster ──────────────────────────────────────────────────────────────

resource "aws_ecs_cluster" "firm" {
  name = "${var.name_prefix}-cluster"

  setting {
    name  = "containerInsights"
    value = "enabled"
  }
}

# ── IAM ──────────────────────────────────────────────────────────────────────

resource "aws_iam_role" "task_execution" {
  name = "${var.name_prefix}-task-execution"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = { Service = "ecs-tasks.amazonaws.com" }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "task_execution" {
  role       = aws_iam_role.task_execution.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

resource "aws_iam_role" "task" {
  name = "${var.name_prefix}-task"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = { Service = "ecs-tasks.amazonaws.com" }
    }]
  })
}

# ── Security Group ───────────────────────────────────────────────────────────

resource "aws_security_group" "firm" {
  name_prefix = "${var.name_prefix}-"
  vpc_id      = data.aws_vpc.default.id

  ingress {
    from_port   = var.mcp_port
    to_port     = var.mcp_port
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "MCP server"
  }

  dynamic "ingress" {
    for_each = var.enable_memory_server ? [1] : []
    content {
      from_port   = var.memory_port
      to_port     = var.memory_port
      protocol    = "tcp"
      cidr_blocks = ["0.0.0.0/0"]
      description = "Memory server"
    }
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# ── CloudWatch Logs ──────────────────────────────────────────────────────────

resource "aws_cloudwatch_log_group" "firm" {
  name              = "/ecs/${var.name_prefix}"
  retention_in_days = 30
}

# ── Task Definition ──────────────────────────────────────────────────────────

locals {
  base_env = [
    { name = "MCP_EXT_HOST", value = "0.0.0.0" },
    { name = "MCP_EXT_PORT", value = tostring(var.mcp_port) },
  ]
  extra_env = [for k, v in var.environment : { name = k, value = v }]
  all_env   = concat(local.base_env, local.extra_env)

  mcp_container = {
    name      = "mcp-server"
    image     = local.mcp_image
    essential = true
    portMappings = [{
      containerPort = var.mcp_port
      hostPort      = var.mcp_port
      protocol      = "tcp"
    }]
    environment = local.all_env
    logConfiguration = {
      logDriver = "awslogs"
      options = {
        "awslogs-group"         = aws_cloudwatch_log_group.firm.name
        "awslogs-region"        = var.region
        "awslogs-stream-prefix" = "mcp"
      }
    }
    healthCheck = {
      command     = ["CMD-SHELL", "python -c \"import urllib.request; urllib.request.urlopen('http://localhost:${var.mcp_port}/health')\""]
      interval    = 30
      timeout     = 5
      retries     = 3
      startPeriod = 60
    }
  }

  memory_container = var.enable_memory_server ? [{
    name      = "memory-server"
    image     = local.memory_image
    essential = false
    portMappings = [{
      containerPort = var.memory_port
      hostPort      = var.memory_port
      protocol      = "tcp"
    }]
    environment = [{ name = "MEMORY_HOST", value = "0.0.0.0" }, { name = "MEMORY_PORT", value = tostring(var.memory_port) }]
    logConfiguration = {
      logDriver = "awslogs"
      options = {
        "awslogs-group"         = aws_cloudwatch_log_group.firm.name
        "awslogs-region"        = var.region
        "awslogs-stream-prefix" = "memory"
      }
    }
  }] : []

  containers = concat([local.mcp_container], local.memory_container)
}

resource "aws_ecs_task_definition" "firm" {
  family                   = "${var.name_prefix}-task"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = tostring(var.cpu)
  memory                   = tostring(var.memory)
  execution_role_arn       = aws_iam_role.task_execution.arn
  task_role_arn            = aws_iam_role.task.arn

  container_definitions = jsonencode(local.containers)
}

# ── ECS Service ──────────────────────────────────────────────────────────────

resource "aws_ecs_service" "firm" {
  name            = "${var.name_prefix}-service"
  cluster         = aws_ecs_cluster.firm.id
  task_definition = aws_ecs_task_definition.firm.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = data.aws_subnets.default.ids
    security_groups  = [aws_security_group.firm.id]
    assign_public_ip = true
  }
}

# ── Outputs ──────────────────────────────────────────────────────────────────

output "mcp_endpoint" {
  description = "MCP server endpoint (use with VS Code MCP settings)"
  value       = "http://<public-ip>:${var.mcp_port}/mcp"
}

output "memory_endpoint" {
  description = "Memory server endpoint"
  value       = var.enable_memory_server ? "http://<public-ip>:${var.memory_port}" : "disabled"
}

output "service_name" {
  description = "ECS service name for CLI management"
  value       = aws_ecs_service.firm.name
}

output "cluster_name" {
  description = "ECS cluster name"
  value       = aws_ecs_cluster.firm.name
}
