terraform {
  required_version = ">= 1.6.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.region
}

locals {
  dvc_bucket_name    = "wafer-project-pm29"
  dvc_bucket_prefix  = "dvc-registry/"
  mlflow_artifacts   = "mlflow-artifacts/"
  tags = {
    Project = var.project_prefix
  }
}

resource "aws_vpc" "main" {
  cidr_block           = var.vpc_cidr
  enable_dns_support   = true
  enable_dns_hostnames = true
  tags                 = local.tags
}

resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.main.id
  tags   = local.tags
}

resource "aws_subnet" "public" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = var.public_subnet_cidr
  map_public_ip_on_launch = true
  availability_zone       = "${var.region}a"
  tags                    = merge(local.tags, { Name = "${var.project_prefix}-public" })
}

resource "aws_subnet" "public_b" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = var.public_subnet_cidr_b
  map_public_ip_on_launch = true
  availability_zone       = "${var.region}b"
  tags                    = merge(local.tags, { Name = "${var.project_prefix}-public-b" })
}

resource "aws_subnet" "private" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = var.private_subnet_cidr
  availability_zone = "${var.region}a"
  tags              = merge(local.tags, { Name = "${var.project_prefix}-private" })
}

resource "aws_eip" "nat" {
  count  = var.enable_nat_gateway ? 1 : 0
  domain = "vpc"
}

resource "aws_nat_gateway" "nat" {
  count         = var.enable_nat_gateway ? 1 : 0
  allocation_id = aws_eip.nat[0].id
  subnet_id     = aws_subnet.public.id
  tags          = local.tags
}

resource "aws_route_table" "public_rt" {
  vpc_id = aws_vpc.main.id
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.igw.id
  }
}

resource "aws_route_table_association" "public_assoc" {
  subnet_id      = aws_subnet.public.id
  route_table_id = aws_route_table.public_rt.id
}

resource "aws_route_table_association" "public_b_assoc" {
  subnet_id      = aws_subnet.public_b.id
  route_table_id = aws_route_table.public_rt.id
}

resource "aws_route_table" "private_rt" {
  vpc_id = aws_vpc.main.id

  dynamic "route" {
    for_each = var.enable_nat_gateway ? [1] : []
    content {
      cidr_block     = "0.0.0.0/0"
      nat_gateway_id = aws_nat_gateway.nat[0].id
    }
  }
}

resource "aws_route_table_association" "private_assoc" {
  subnet_id      = aws_subnet.private.id
  route_table_id = aws_route_table.private_rt.id
}

resource "aws_vpc_endpoint" "s3" {
  count        = var.enable_s3_vpc_endpoint ? 1 : 0
  vpc_id       = aws_vpc.main.id
  service_name = "com.amazonaws.${var.region}.s3"
  route_table_ids = [
    aws_route_table.private_rt.id,
  ]
}

resource "aws_security_group" "alb" {
  count       = var.enable_alb ? 1 : 0
  name        = "${var.project_prefix}-alb"
  description = "ALB security group"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_security_group" "ec2_api" {
  name   = "${var.project_prefix}-ec2-api"
  vpc_id = aws_vpc.main.id

  dynamic "ingress" {
    for_each = var.enable_alb ? [1] : []
    content {
      from_port       = 8000
      to_port         = 8000
      protocol        = "tcp"
      security_groups = [aws_security_group.alb[0].id]
    }
  }

  dynamic "ingress" {
    for_each = var.enable_alb ? [] : [1]
    content {
      from_port   = 8000
      to_port     = 8000
      protocol    = "tcp"
      cidr_blocks = [var.api_ingress_cidr]
    }
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_security_group" "rds" {
  name   = "${var.project_prefix}-rds"
  vpc_id = aws_vpc.main.id

  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.ec2_api.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_s3_bucket" "wafer_data" {
  bucket = local.dvc_bucket_name
  tags   = local.tags
}

resource "aws_s3_bucket_versioning" "wafer_data_versioning" {
  bucket = aws_s3_bucket.wafer_data.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "wafer_data_enc" {
  bucket = aws_s3_bucket.wafer_data.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "wafer_logs_ttl" {
  bucket = aws_s3_bucket.wafer_data.id

  rule {
    id     = "logs-90-days"
    status = "Enabled"

    filter {
      prefix = "logs/"
    }

    expiration {
      days = 90
    }
  }
}

resource "aws_db_subnet_group" "db_subnets" {
  name       = "${lower(var.project_prefix)}-db-subnets"
  subnet_ids = [aws_subnet.public.id, aws_subnet.public_b.id]
}

resource "aws_db_instance" "postgres" {
  identifier             = "wafer-project-db"
  allocated_storage      = 20
  storage_type           = "gp2"
  engine                 = "postgres"
  engine_version         = "16"
  instance_class         = "db.t3.micro"
  db_name                = "wafer_project"
  username               = "wafer_user"
  password               = var.db_password
  db_subnet_group_name   = aws_db_subnet_group.db_subnets.name
  vpc_security_group_ids = [aws_security_group.rds.id]
  publicly_accessible    = false
  skip_final_snapshot    = true
  backup_retention_period = 1
  tags                   = local.tags
}

resource "aws_secretsmanager_secret" "api_env" {
  name = "${var.project_prefix}_API_ENV"
}

resource "aws_secretsmanager_secret_version" "api_env_values" {
  secret_id = aws_secretsmanager_secret.api_env.id
  secret_string = jsonencode({
    WAFER_PROJECT_API_KEY                = var.api_key
    WAFER_PROJECT_DB_HOST                = aws_db_instance.postgres.address
    WAFER_PROJECT_DB_PORT                = 5432
    WAFER_PROJECT_DB_NAME                = aws_db_instance.postgres.db_name
    WAFER_PROJECT_DB_USER                = aws_db_instance.postgres.username
    WAFER_PROJECT_DB_PASSWORD            = var.db_password
    WAFER_PROJECT_AWS_REGION             = var.region
    WAFER_PROJECT_S3_BATCH_BUCKET        = local.dvc_bucket_name
    WAFER_PROJECT_S3_DVC_URI             = "s3://${local.dvc_bucket_name}/${local.dvc_bucket_prefix}"
    WAFER_PROJECT_S3_MLFLOW_ARTIFACTS_URI = "s3://${local.dvc_bucket_name}/${local.mlflow_artifacts}"
    WAFER_PROJECT_MLFLOW_TRACKING_URI    = "http://mlflow.internal:5000"
    WAFER_PROJECT_RUN_OWNER              = var.run_owner
    WAFER_PROJECT_DVC_VERSION_ID         = var.dvc_version_id
  })
}

resource "aws_cloudwatch_log_group" "api" {
  name              = "/wafer-project/api"
  retention_in_days = 90
}

resource "aws_iam_role" "ec2_api_role" {
  name = "${var.project_prefix}-ec2-api-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "ec2.amazonaws.com"
      }
    }]
  })
}

resource "aws_iam_instance_profile" "ec2_api_profile" {
  name = "${var.project_prefix}-ec2-api-profile"
  role = aws_iam_role.ec2_api_role.name
}

resource "aws_iam_role_policy" "ec2_api_policy" {
  name = "${var.project_prefix}-ec2-api-policy"
  role = aws_iam_role.ec2_api_role.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:ListBucket"
        ]
        Resource = [
          aws_s3_bucket.wafer_data.arn,
          "${aws_s3_bucket.wafer_data.arn}/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue"
        ]
        Resource = [aws_secretsmanager_secret.api_env.arn]
      },
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = ["${aws_cloudwatch_log_group.api.arn}:*"]
      }
    ]
  })
}

resource "aws_instance" "api" {
  ami                    = var.api_ami_id
  instance_type          = var.api_instance_type
  subnet_id              = var.use_private_api_subnet ? aws_subnet.private.id : aws_subnet.public.id
  vpc_security_group_ids = [aws_security_group.ec2_api.id]
  iam_instance_profile   = aws_iam_instance_profile.ec2_api_profile.name

  user_data = <<-EOF
              #!/bin/bash
              set -e
              apt-get update -y
              apt-get install -y docker.io
              systemctl enable docker
              systemctl start docker
              docker pull public.ecr.aws/docker/library/python:3.9-slim
              EOF

  tags = merge(local.tags, { Name = "${var.project_prefix}-api-ec2" })
}

resource "aws_lb" "api" {
  count              = var.enable_alb ? 1 : 0
  name               = "wafer-project-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb[0].id]
  subnets            = [aws_subnet.public.id, aws_subnet.public_b.id]

  access_logs {
    bucket  = aws_s3_bucket.wafer_data.id
    prefix  = "logs/alb"
    enabled = true
  }
}

resource "aws_lb_target_group" "api" {
  count    = var.enable_alb ? 1 : 0
  name     = "wafer-project-tg"
  port     = 8000
  protocol = "HTTP"
  vpc_id   = aws_vpc.main.id

  health_check {
    enabled = true
    path    = "/health"
  }
}

resource "aws_lb_target_group_attachment" "api_ec2" {
  count            = var.enable_alb ? 1 : 0
  target_group_arn = aws_lb_target_group.api[0].arn
  target_id        = aws_instance.api.id
  port             = 8000
}

resource "aws_lb_listener" "http" {
  count             = var.enable_alb ? 1 : 0
  load_balancer_arn = aws_lb.api[0].arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.api[0].arn
  }
}

resource "aws_sns_topic" "pipeline_alerts" {
  count = var.enable_observability ? 1 : 0
  name = "${var.project_prefix}-pipeline-alerts"
}

resource "aws_sns_topic_subscription" "email_alert" {
  count     = var.enable_observability ? 1 : 0
  topic_arn = aws_sns_topic.pipeline_alerts[0].arn
  protocol  = "email"
  endpoint  = var.alert_email
}

resource "aws_cloudwatch_metric_alarm" "lambda_errors" {
  count               = var.enable_observability ? 1 : 0
  alarm_name          = "${var.project_prefix}-lambda-errors"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "Errors"
  namespace           = "AWS/Lambda"
  period              = 300
  statistic           = "Sum"
  threshold           = 0
  alarm_description   = "Alert on lambda ingestion failures"
  treat_missing_data  = "notBreaching"
  alarm_actions       = [aws_sns_topic.pipeline_alerts[0].arn]

  dimensions = {
    FunctionName = "wafer-batch-ingestion"
  }
}

resource "aws_cloudwatch_dashboard" "api_dashboard" {
  count          = var.enable_observability ? 1 : 0
  dashboard_name = "wafer-project-observability"
  dashboard_body = jsonencode({
    widgets = [
      {
        type = "metric"
        x = 0
        y = 0
        width = 12
        height = 6
        properties = {
          title = "ALB Target Response Time"
          metrics = [["AWS/ApplicationELB", "TargetResponseTime"]]
          stat = "p95"
          period = 300
          region = var.region
        }
      },
      {
        type = "metric"
        x = 12
        y = 0
        width = 12
        height = 6
        properties = {
          title = "EC2 CPU Utilization"
          metrics = [["AWS/EC2", "CPUUtilization"]]
          stat = "Average"
          period = 300
          region = var.region
        }
      }
    ]
  })
}
