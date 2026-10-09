# Terraform setup for deploying the Autonomous Cost Optimizer on AWS (ECS Fargate + EventBridge)

terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

variable "aws_region" {
  type    = string
  default = "us-east-1"
}

variable "environment" {
  type    = string
  default = "production"
}

# 1. ECR Repository for Agent Container Image
resource "aws_ecr_repository" "agent_repo" {
  name                 = "cloud-cost-optimizer-agent"
  image_tag_mutability = "MUTABLE"
  force_delete         = true
  image_scanning_configuration {
    scan_on_push = true
  }
}

# 2. ECS Cluster
resource "aws_ecs_cluster" "optimizer_cluster" {
  name = "finops-agent-cluster-${var.environment}"
}

# 3. CloudWatch Log Group
resource "aws_cloudwatch_log_group" "agent_logs" {
  name              = "/ecs/cloud-cost-optimizer"
  retention_in_days = 30
}

# 4. Secrets Manager for LLM API Keys
resource "aws_secretsmanager_secret" "llm_api_key" {
  name                    = "finops-agent/llm-api-keys"
  recovery_window_in_days = 0
}

# 5. ECS Task Definition (Fargate)
resource "aws_ecs_task_definition" "optimizer_task" {
  family                   = "cloud-cost-optimizer"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = "512"
  memory                   = "1024"
  execution_role_arn       = aws_iam_role.ecs_execution_role.arn
  task_role_arn            = aws_iam_role.agent_task_role.arn

  container_definitions = jsonencode([
    {
      name      = "cost-optimizer-agent"
      image     = "${aws_ecr_repository.agent_repo.repository_url}:latest"
      essential = true
      environment = [
        { name = "ENVIRONMENT", value = var.environment },
        { name = "AWS_DEFAULT_REGION", value = var.aws_region }
      ]
      secrets = [
        {
          name      = "ANTHROPIC_API_KEY"
          valueFrom = "${aws_secretsmanager_secret.llm_api_key.arn}:ANTHROPIC_API_KEY::"
        }
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.agent_logs.name
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "ecs"
        }
      }
    }
  ])
}

# 6. EventBridge Rule: Trigger Agent Daily at 06:00 UTC
resource "aws_cloudwatch_event_rule" "daily_schedule" {
  name                = "daily-cost-optimization-run"
  description         = "Triggers the Autonomous Cost Optimizer agent daily"
  schedule_expression = "cron(0 6 * * ? *)"
}

# 7. VPC & Subnet Lookups for Fargate Task Execution
data "aws_vpc" "default" {
  default = true
}

data "aws_subnets" "default" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
}

# 8. EventBridge Target to trigger ECS Task
resource "aws_cloudwatch_event_target" "ecs_target" {
  rule     = aws_cloudwatch_event_rule.daily_schedule.name
  arn      = aws_ecs_cluster.optimizer_cluster.arn
  role_arn = aws_iam_role.eventbridge_ecs_role.arn

  ecs_target {
    task_count          = 1
    task_definition_arn = aws_ecs_task_definition.optimizer_task.arn
    launch_type         = "FARGATE"
    network_configuration {
      subnets          = data.aws_subnets.default.ids
      assign_public_ip = true
    }
  }
}
