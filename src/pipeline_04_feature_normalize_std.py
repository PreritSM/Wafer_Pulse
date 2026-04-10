import logging
import os

import joblib
import pandas as pd
from sklearn.preprocessing import StandardScaler

from src.pipeline_01_config_setup_fun import read_params

logger = logging.getLogger(__name__)


def feature_scaling(config):
    """
    Standardize features with StandardScaler and persist the fitted scaler.
    """
    csv_path = os.path.join(
        config["data_preparation"]["preprocessed_data_dir"], "preprocessed_secom_data.csv"
    )
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Preprocessed data not found: {csv_path}")

    logger.info("Loading preprocessed data from %s", csv_path)
    df = pd.read_csv(csv_path)
    y = df["Output"].copy()
    df.drop("Output", axis=1, inplace=True)

    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(df)
    scaler_path = os.path.join(config["artifacts_dir"]["general"], "feature_scaler.pkl")
    joblib.dump(scaler, scaler_path)
    logger.info("Scaler fitted and saved to %s", scaler_path)

    df_scaled = pd.DataFrame(scaled_features, columns=df.columns)
    df_scaled["Output"] = y
    out_path = os.path.join(
        config["data_preparation"]["preprocessed_data_dir"], "scaled_secom_data.csv"
    )
    df_scaled.to_csv(out_path, index=False)
    logger.info("Scaled data saved to %s — shape: %s", out_path, df_scaled.shape)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s"
    )
    config = read_params(os.path.join("config", "params.yaml"))
    feature_scaling(config)
    logger.info("Feature scaling completed.")
