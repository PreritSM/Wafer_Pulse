output "vpc_id" {
  value = aws_vpc.main.id
}

output "private_subnet_id" {
  value = aws_subnet.private.id
}

output "public_subnet_id" {
  value = aws_subnet.public.id
}

output "public_subnet_b_id" {
  value = aws_subnet.public_b.id
}

output "dvc_remote_uri" {
  value = "s3://wafer-project-pm29/dvc-registry/"
}

output "mlflow_artifacts_uri" {
  value = "s3://wafer-project-pm29/mlflow-artifacts/"
}

output "rds_endpoint" {
  value = aws_db_instance.postgres.address
}

output "api_alb_dns_name" {
  value = try(aws_lb.api[0].dns_name, null)
}

output "api_ec2_public_dns" {
  value = aws_instance.api.public_dns
}

output "api_ec2_public_ip" {
  value = aws_instance.api.public_ip
}
