import boto3

from src.infrastructure.settings import get_settings


def get_s3_client():
    settings = get_settings()
    return boto3.client("s3", region_name=settings.aws_region)
