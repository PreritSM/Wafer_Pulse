import os
import tempfile
import unittest

import numpy as np
import pandas as pd
import yaml

from src.pipeline_01_config_setup_fun import read_params
from src.pipeline_03_data_preprocessing import (
    missing_value_imputation,
    target_variable_encoding,
)
from src.pipeline_07_model_inference import ModelInference


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_config(tmp_dir: str) -> dict:
    """Minimal config pointing all artifact/data paths at a temp directory."""
    return {
        'base': {'random_state': 42, 'target_col': 'Output'},
        'data_source': {
            'local_data_dir': tmp_dir,
            'raw_combined_data': tmp_dir,
            'Train_Data_dir': tmp_dir,
        },
        'data_preparation': {
            'preprocessed_data_dir': tmp_dir,
            'missing_threshold': 0.5,
            'top_n_features': 3,
        },
        'artifacts_dir': {'general': tmp_dir},
        'saved_models': {'model_dir': tmp_dir},
    }


# ---------------------------------------------------------------------------
# pipeline_01 — config loading
# ---------------------------------------------------------------------------

class TestReadParams(unittest.TestCase):

    def test_loads_valid_yaml(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump({'key': 'value', 'nested': {'a': 1}}, f)
            path = f.name
        try:
            params = read_params(path)
            self.assertEqual(params['key'], 'value')
            self.assertEqual(params['nested']['a'], 1)
        finally:
            os.unlink(path)

    def test_raises_on_missing_file(self):
        with self.assertRaises(FileNotFoundError):
            read_params("/nonexistent/path/params.yaml")


# ---------------------------------------------------------------------------
# pipeline_03 — preprocessing helpers
# ---------------------------------------------------------------------------

class TestTargetVariableEncoding(unittest.TestCase):

    def test_maps_minus_one_to_zero(self):
        y = pd.Series([-1, -1, 1])
        result = target_variable_encoding(y)
        self.assertEqual(result.tolist(), [0, 0, 1])

    def test_maps_one_to_one(self):
        y = pd.Series([1])
        self.assertEqual(target_variable_encoding(y).iloc[0], 1)

    def test_output_length_unchanged(self):
        y = pd.Series([-1, 1, -1, 1, -1])
        self.assertEqual(len(target_variable_encoding(y)), 5)


class TestMissingValueImputation(unittest.TestCase):

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()
        self.config = _make_config(self.tmp_dir)

    def test_no_nulls_after_imputation(self):
        df = pd.DataFrame({'A': [1.0, np.nan, 3.0], 'B': [np.nan, 2.0, 3.0]})
        result = missing_value_imputation(df, self.config)
        self.assertEqual(result.isnull().sum().sum(), 0)

    def test_shape_preserved(self):
        df = pd.DataFrame({'A': [1.0, np.nan], 'B': [np.nan, 2.0]})
        result = missing_value_imputation(df, self.config)
        self.assertEqual(result.shape, df.shape)

    def test_imputes_with_column_mean(self):
        df = pd.DataFrame({'A': [2.0, 4.0, np.nan]})
        result = missing_value_imputation(df, self.config)
        self.assertAlmostEqual(result['A'].iloc[2], 3.0)


# ---------------------------------------------------------------------------
# pipeline_07 — ModelInference
# ---------------------------------------------------------------------------

class TestModelInference(unittest.TestCase):

    def test_load_model_raises_for_missing_file(self):
        inference = ModelInference("/nonexistent/model.pkl")
        with self.assertRaises(FileNotFoundError):
            inference.load_model()

    def test_inference_raises_when_model_not_loaded(self):
        inference = ModelInference("/nonexistent/model.pkl")
        with self.assertRaises(ValueError, msg="Should raise when model is None"):
            inference.model_inference(np.zeros((1, 60)))

    def test_inference_raises_on_none_input(self):
        inference = ModelInference("/nonexistent/model.pkl")
        inference.model = object()  # anything non-None to pass the first guard
        with self.assertRaises((ValueError, AttributeError)):
            inference.model_inference(None)

    def test_inference_raises_on_wrong_feature_count(self):
        """model_inference must reject arrays with != 60 features."""
        import joblib
        import sklearn.ensemble

        with tempfile.TemporaryDirectory() as tmp:
            # Train a trivial model to dump
            from sklearn.ensemble import RandomForestClassifier
            clf = RandomForestClassifier(n_estimators=1, random_state=0)
            X = np.random.rand(10, 60)
            y = np.array([0, 1] * 5)
            clf.fit(X, y)
            model_path = os.path.join(tmp, "model.pkl")
            joblib.dump(clf, model_path)

            inference = ModelInference(model_path)
            inference.load_model()
            with self.assertRaises(ValueError):
                inference.model_inference(np.zeros((1, 30)))  # wrong count

    def test_inference_returns_predictions_for_valid_input(self):
        """Happy path: 60-feature input returns a prediction array."""
        import joblib
        from sklearn.ensemble import RandomForestClassifier

        with tempfile.TemporaryDirectory() as tmp:
            clf = RandomForestClassifier(n_estimators=1, random_state=0)
            X = np.random.rand(10, 60)
            y = np.array([0, 1] * 5)
            clf.fit(X, y)
            model_path = os.path.join(tmp, "model.pkl")
            joblib.dump(clf, model_path)

            inference = ModelInference(model_path)
            inference.load_model()
            preds = inference.model_inference(np.zeros((3, 60)))
            self.assertEqual(len(preds), 3)


if __name__ == '__main__':
    unittest.main()
