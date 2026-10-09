# IAM Roles & Least-Privilege Policies for Cost Optimizer Agent

# 1. ECS Task Execution Role (Pull from ECR & write logs)
resource "aws_iam_role" "ecs_execution_role" {
  name = "finops-agent-ecs-execution-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action    = "sts:AssumeRole"
      Effect    = "Allow"
      Principal = { Service = "ecs-tasks.amazonaws.com" }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_execution_attach" {
  role       = aws_iam_role.ecs_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

# Allow ECS Execution Agent to pull secrets from Secrets Manager
resource "aws_iam_policy" "ecs_execution_secrets_policy" {
  name        = "FinOpsExecutionSecretsPolicy"
  description = "Allows ECS Execution Role to fetch secret values for container env vars"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue"
        ]
        Resource = aws_secretsmanager_secret.llm_api_key.arn
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_execution_secrets_attach" {
  role       = aws_iam_role.ecs_execution_role.name
  policy_arn = aws_iam_policy.ecs_execution_secrets_policy.arn
}

# 2. Agent Runtime Task Role (Access AWS APIs for FinOps & Telemetry)
resource "aws_iam_role" "agent_task_role" {
  name = "finops-agent-task-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action    = "sts:AssumeRole"
      Effect    = "Allow"
      Principal = { Service = "ecs-tasks.amazonaws.com" }
    }]
  })
}

# Custom Least-Privilege Policy for FinOps Agent
resource "aws_iam_policy" "agent_permissions" {
  name        = "FinOpsAgentLeastPrivilegePolicy"
  description = "Allows read access to cost/metrics and safe remediation"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      # Read-only Telemetry & Cost APIs
      {
        Effect = "Allow"
        Action = [
          "ce:GetCostAndUsage",
          "ce:GetCostForecast",
          "ce:GetReservationUtilization",
          "ce:GetSavingsPlansUtilization",
          "cloudwatch:GetMetricStatistics",
          "cloudwatch:GetMetricData",
          "cloudwatch:ListMetrics",
          "ec2:DescribeInstances",
          "ec2:DescribeVolumes",
          "ec2:DescribeSnapshots",
          "ec2:DescribeAddresses",
          "organizations:ListAccounts"
        ]
        Resource = "*"
      },
      # Guardrailed Remediation (Snapshots & non-prod volume cleanup)
      {
        Effect = "Allow"
        Action = [
          "ec2:CreateSnapshot",
          "ec2:CreateTags",
          "ec2:DeleteVolume"
        ]
        Resource = "*"
        Condition = {
          StringEquals = {
            "aws:RequestTag/ManagedBy": "AutonomousCostOptimizer"
          }
        }
      },
      # Secret retrieval
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue"
        ]
        Resource = aws_secretsmanager_secret.llm_api_key.arn
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "agent_policy_attach" {
  role       = aws_iam_role.agent_task_role.name
  policy_arn = aws_iam_policy.agent_permissions.arn
}

# 3. EventBridge IAM Role to Run ECS Task
resource "aws_iam_role" "eventbridge_ecs_role" {
  name = "finops-agent-eventbridge-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action    = "sts:AssumeRole"
      Effect    = "Allow"
      Principal = { Service = "events.amazonaws.com" }
    }]
  })
}

resource "aws_iam_policy" "eventbridge_run_task" {
  name = "FinOpsEventBridgeRunTaskPolicy"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = ["ecs:RunTask"]
        Resource = ["*"]
      },
      {
        Effect   = "Allow"
        Action   = ["iam:PassRole"]
        Resource = [
          aws_iam_role.ecs_execution_role.arn,
          aws_iam_role.agent_task_role.arn
        ]
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "eventbridge_attach" {
  role       = aws_iam_role.eventbridge_ecs_role.name
  policy_arn = aws_iam_policy.eventbridge_run_task.arn
}
