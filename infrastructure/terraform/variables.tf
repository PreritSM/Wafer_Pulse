variable "project_prefix" {
  description = "Resource prefix"
  type        = string
  default     = "WAFER_PROJECT"
}

variable "region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "vpc_cidr" {
  description = "VPC CIDR"
  type        = string
  default     = "10.0.0.0/16"
}

variable "public_subnet_cidr" {
  description = "Public subnet CIDR"
  type        = string
  default     = "10.0.1.0/24"
}

variable "public_subnet_cidr_b" {
  description = "Second public subnet CIDR (for ALB/RDS subnet group requirements)"
  type        = string
  default     = "10.0.3.0/24"
}

variable "private_subnet_cidr" {
  description = "Private subnet CIDR"
  type        = string
  default     = "10.0.2.0/24"
}

variable "enable_nat_gateway" {
  description = "Enable NAT gateway for private subnet egress"
  type        = bool
  default     = false
}

variable "enable_alb" {
  description = "Enable internet-facing ALB in front of API EC2"
  type        = bool
  default     = false
}

variable "enable_s3_vpc_endpoint" {
  description = "Enable S3 VPC endpoint for private route table"
  type        = bool
  default     = false
}

variable "enable_observability" {
  description = "Enable optional dashboard, SNS topic/subscription, and metric alarm"
  type        = bool
  default     = false
}

variable "use_private_api_subnet" {
  description = "Place API EC2 in private subnet (requires NAT/other egress setup)"
  type        = bool
  default     = false
}

variable "api_ingress_cidr" {
  description = "Allowed CIDR to access API EC2 directly when ALB is disabled"
  type        = string
  default     = "0.0.0.0/0"
}

variable "db_password" {
  description = "RDS password"
  type        = string
  sensitive   = true
}

variable "api_key" {
  description = "External test API key"
  type        = string
  sensitive   = true
}

variable "run_owner" {
  description = "MLflow run owner tag"
  type        = string
}

variable "dvc_version_id" {
  description = "Current DVC version identifier"
  type        = string
}

variable "api_ami_id" {
  description = "AMI ID for API EC2 instance"
  type        = string
}

variable "api_instance_type" {
  description = "EC2 instance type for API service"
  type        = string
  default     = "t3.micro"
}

variable "alert_email" {
  description = "Email endpoint for SNS alerts"
  type        = string
  default     = "noreply@example.com"
}
