import os
import sys

import numpy as np
from flask import Flask, jsonify, request

# Allow imports from src/ when running directly
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pipeline_01_config_setup_fun import read_params
from pipeline_07_model_inference import ModelInference
from api.schemas import (
    BatchPredictRequest,
    BatchPredictResponse,
    HealthResponse,
    PredictRequest,
    PredictResponse,
)

app = Flask(__name__)

# ---------------------------------------------------------------------------
# Model loading — done once at startup
# ---------------------------------------------------------------------------

_CONFIG_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "config",
    "params.yaml",
)
_config = read_params(_CONFIG_PATH)
_model_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    _config["saved_models"]["model_dir"],
    "best_model.pkl",
)

_inference = ModelInference(_model_path)
try:
    _inference.load_model()
    _model_loaded = True
except FileNotFoundError:
    _model_loaded = False


def _label(pred: int) -> str:
    return "Defective" if pred == 1 else "Good"


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route("/health", methods=["GET"])
def health():
    resp = HealthResponse(
        status="ok" if _model_loaded else "model_not_found",
        model_loaded=_model_loaded,
        model_path=_model_path,
    )
    return jsonify(resp.to_dict()), 200


@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json(silent=True)
    if data is None:
        return jsonify({"error": "Request body must be JSON"}), 400

    req = PredictRequest.from_dict(data)
    err = req.validate()
    if err:
        return jsonify({"error": err}), 422

    if not _model_loaded:
        return jsonify({"error": "Model not loaded"}), 503

    input_array = np.array([req.sensor_readings])
    prediction = int(_inference.model_inference(input_array)[0])
    resp = PredictResponse(prediction=prediction, label=_label(prediction))
    return jsonify(resp.to_dict()), 200


@app.route("/predict/batch", methods=["POST"])
def predict_batch():
    data = request.get_json(silent=True)
    if data is None:
        return jsonify({"error": "Request body must be JSON"}), 400

    req = BatchPredictRequest.from_dict(data)
    err = req.validate()
    if err:
        return jsonify({"error": err}), 422

    if not _model_loaded:
        return jsonify({"error": "Model not loaded"}), 503

    input_array = np.array(req.wafers)
    raw_predictions = _inference.model_inference(input_array)

    results = [{"prediction": int(p), "label": _label(int(p))} for p in raw_predictions]
    defective = sum(1 for r in results if r["prediction"] == 1)
    resp = BatchPredictResponse(
        predictions=results,
        total=len(results),
        defective_count=defective,
    )
    return jsonify(resp.to_dict()), 200


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    app.run(host="0.0.0.0", port=port, debug=debug)
