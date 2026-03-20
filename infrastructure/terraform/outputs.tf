output "vpc_id" {
  value = aws_vpc.main.id
}

output "private_subnet_id" {
  value = aws_subnet.private.id
}

output "public_subnet_id" {
  value = aws_subnet.public.id
}

output "dvc_remote_uri" {
  value = "s3://wafer-data/dvc-registry/"
}

output "mlflow_artifacts_uri" {
  value = "s3://wafer-data/mlflow-artifacts/"
}

output "rds_endpoint" {
  value = aws_db_instance.postgres.address
}

output "api_alb_dns_name" {
  value = aws_lb.api.dns_name
}
