from io import StringIO
from urllib.parse import unquote_plus

import pandas as pd

from src.infrastructure.aws_clients import get_s3_client
from src.infrastructure.db import init_db, save_prediction
from src.infrastructure.model_runtime import ModelRuntime
from src.infrastructure.retry import with_exponential_backoff
from src.infrastructure.settings import validate_required_settings


def _download_csv_text(bucket: str, key: str) -> str:
    client = get_s3_client()
    response = with_exponential_backoff(client.get_object, Bucket=bucket, Key=key, retries=3)
    body = response["Body"].read().decode("utf-8")
    return body


def lambda_handler(event, context):
    """S3-triggered batch inference entrypoint with 10MB payload guard."""
    del context
    settings = validate_required_settings()
    init_db()
    runtime = ModelRuntime()

    processed = []
    for record in event.get("Records", []):
        s3_record = record.get("s3", {})
        bucket = s3_record.get("bucket", {}).get("name", settings.s3_batch_bucket)
        obj = s3_record.get("object", {})
        key = unquote_plus(obj.get("key", ""))
        size = int(obj.get("size", 0))

        if size > settings.batch_limit_bytes:
            processed.append({"key": key, "status": "skipped", "reason": "size_limit"})
            continue

        csv_text = _download_csv_text(bucket, key)
        df = pd.read_csv(StringIO(csv_text))

        if df.shape[1] < 591:
            processed.append({"key": key, "status": "failed", "reason": "invalid_column_count"})
            continue

        for _, row in df.iterrows():
            sensors = [float(value) for value in row.iloc[:591].tolist()]
            prediction = runtime.predict(sensors)
            save_prediction(
                payload={"s3_bucket": bucket, "s3_key": key, "sensors": sensors},
                label=prediction.label,
                confidence=prediction.confidence,
                raw_prediction=prediction.raw_prediction,
                source="lambda",
            )

        processed.append({"key": key, "status": "processed", "rows": int(df.shape[0])})

    return {"processed": processed}
