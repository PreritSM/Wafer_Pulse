import os
import unittest

from src.api.schemas import PredictRequest, BatchPredictRequest
from src.infrastructure.settings import AppSettings


class TestPredictRequestSchema(unittest.TestCase):

    def test_valid_request_accepts_60_values(self):
        req = PredictRequest.from_dict({"sensor_readings": [0.1] * 60})
        self.assertIsNone(req.validate())
        self.assertEqual(len(req.sensor_readings), 60)

    def test_rejects_wrong_length(self):
        req = PredictRequest.from_dict({"sensor_readings": [0.1] * 59})
        self.assertIsNotNone(req.validate())

    def test_rejects_non_numeric_values(self):
        req = PredictRequest.from_dict({"sensor_readings": ["a"] * 60})
        self.assertIsNotNone(req.validate())

    def test_rejects_missing_field(self):
        req = PredictRequest.from_dict({})
        self.assertIsNotNone(req.validate())


class TestBatchPredictRequestSchema(unittest.TestCase):

    def test_valid_batch_accepts_multiple_wafers(self):
        req = BatchPredictRequest.from_dict({"wafers": [[0.1] * 60, [0.2] * 60]})
        self.assertIsNone(req.validate())
        self.assertEqual(len(req.wafers), 2)

    def test_rejects_empty_batch(self):
        req = BatchPredictRequest.from_dict({"wafers": []})
        self.assertIsNotNone(req.validate())

    def test_rejects_row_with_wrong_length(self):
        req = BatchPredictRequest.from_dict({"wafers": [[0.1] * 60, [0.1] * 55]})
        self.assertIsNotNone(req.validate())


class TestSettingsValidation(unittest.TestCase):

    def test_settings_fail_without_required_values(self):
        for key in [
            "WAFER_PROJECT_API_KEY",
            "WAFER_PROJECT_S3_BATCH_BUCKET",
            "WAFER_PROJECT_DB_HOST",
            "WAFER_PROJECT_DB_NAME",
            "WAFER_PROJECT_DB_USER",
            "WAFER_PROJECT_DB_PASSWORD",
            "WAFER_PROJECT_MLFLOW_TRACKING_URI",
            "WAFER_PROJECT_RUN_OWNER",
            "WAFER_PROJECT_DVC_VERSION_ID",
        ]:
            os.environ.pop(key, None)

        with self.assertRaises(Exception):
            AppSettings()
