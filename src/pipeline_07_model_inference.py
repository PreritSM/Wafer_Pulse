import argparse
import logging
import os
import pickle
from datetime import datetime

import numpy as np
import pandas as pd

from pipeline_01_config_setup_fun import read_params

logger = logging.getLogger(__name__)

EXPECTED_FEATURES = 60


class ModelInference:
    """Load a serialized model and run predictions against pre-scaled feature vectors."""

    def __init__(self, model_path: str):
        self.model_path = model_path
        self.model = None

    def load_model(self):
        """Load the trained model from disk."""
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"Model not found at: {self.model_path}")
        with open(self.model_path, "rb") as f:
            self.model = pickle.load(f)
        logger.info("Model loaded from %s — type: %s", self.model_path, type(self.model).__name__)
        return self.model

    def model_inference(self, input_data) -> np.ndarray:
        """
        Run predictions on input_data.

        Parameters
        ----------
        input_data : array-like of shape (n_samples, 60)
            Pre-scaled feature vectors (output of StandardScaler + MI feature selection).

        Returns
        -------
        np.ndarray of predictions (-1 = Good, 1 = Defective)
        """
        if self.model is None:
            raise ValueError("Model is not loaded. Call load_model() first.")
        if input_data is None:
            raise ValueError("input_data cannot be None.")

        arr = np.array(input_data)
        if arr.ndim == 1:
            arr = arr.reshape(1, -1)
        if arr.shape[1] != EXPECTED_FEATURES:
            raise ValueError(
                f"Expected {EXPECTED_FEATURES} features per sample, got {arr.shape[1]}."
            )

        logger.info("Running inference on %d sample(s).", arr.shape[0])
        predictions = self.model.predict(arr)
        return predictions


def main(data_init=False):
    """Run model inference, optionally using built-in dummy data for smoke-testing."""
    config = read_params(os.path.join("config", "params.yaml"))
    model_path = os.path.join(config["saved_models"]["model_dir"], "best_model.pkl")

    inference = ModelInference(model_path)
    inference.load_model()

    if not data_init:
        raise ValueError(
            "No input data provided. Pass --dummy_data for a smoke test, "
            "or supply real pre-scaled data programmatically."
        )

    # Dummy row: 60 pre-scaled feature values used for smoke testing only.
    input_data = pd.DataFrame([[
        -0.1355199558643293, -1.3974104675213597, -0.0436636951368608,
        0.4962305571742278, 0.1901422094611682, 0.0344104039648007,
        0.6564202108157732, 0.4110763859335697, 0.5697668111091828,
        -0.1205176348942463, -0.1268390912515736, 2.033487676053904,
        -0.6456089814151296, -1.7682951425913402, -0.05187288745891,
        -0.0358360893252537, -0.2202470920509122, 0.3170877837899783,
        0.3385491955249182, 2.6613961833338395, 1.5145001106248855e-16,
        -0.0892606604731885, -0.0158822800665333, 0.3100774306463221,
        -0.2297974549854701, 0.1923145128256107, -0.3307407574314417,
        -0.2266652381262637, 0.6417098373049347, -0.0314177396168879,
        -1.1485445717473473, -0.2513318627163896, -0.5637900930104123,
        0.2365433704046494, -0.1954856245733606, 0.1747984367759543,
        -7.039347660977129e-16, -0.0509234675052388, 0.5313336573410947,
        -0.4119465291500894, -0.3060906692044917, -0.8513741983087512,
        2.931766649410934, 0.0, -1.1093000717285182, -0.0254575692209623,
        -0.8448490721380661, 1.1891067028901108, 0.1959283143918466,
        -0.115419713262912, -0.9188416579914352, -0.0240553034907226,
        -3.371044220675002e-15, -0.8060787816829231, -0.2771197385149884,
        0.6995686940763757, -0.0356154479842456, -0.5087965232639861,
        0.4194327961009655, 0.5375705950805532,
    ]])
    logger.info("Using dummy input data for smoke test.")

    predictions = inference.model_inference(input_data)
    logger.info("Predictions: %s", predictions)

    predictions_saved = {
        "Inference_Time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "Input_data": input_data.iloc[0].tolist(),
        "Prediction": predictions.tolist(),
    }

    os.makedirs("data/Prediction_Output_File", exist_ok=True)
    saved_path = os.path.join("data/Prediction_Output_File", "Predictions.csv")
    file_exists = os.path.exists(saved_path)
    pd.DataFrame([predictions_saved]).to_csv(
        saved_path,
        index=False,
        mode='a' if file_exists else 'w',
        header=not file_exists,
    )
    logger.info("Predictions saved to %s", saved_path)
    return inference


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    parser = argparse.ArgumentParser()
    parser.add_argument("--dummy_data", action="store_true", help="Use dummy input data for smoke test")
    args = parser.parse_args()
    main(data_init=args.dummy_data)
