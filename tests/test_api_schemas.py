import os
import unittest

from pydantic import ValidationError

from src.api.schemas import PredictRequest
from src.infrastructure.settings import AppSettings


class TestApiSchemas(unittest.TestCase):

    def test_predict_request_requires_591_values(self):
        payload = {"sensors": [0.1] * 591}
        req = PredictRequest(**payload)
        self.assertEqual(len(req.sensors), 591)

    def test_predict_request_rejects_invalid_length(self):
        with self.assertRaises(ValidationError):
            PredictRequest(sensors=[0.1] * 590)


class TestSettingsValidation(unittest.TestCase):

    def test_settings_fail_without_required_values(self):
        os.environ.pop("WAFER_PROJECT_API_KEY", None)
        with self.assertRaises(ValidationError):
            AppSettings()
