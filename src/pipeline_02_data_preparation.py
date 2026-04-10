import logging
import os
from pathlib import Path

import pandas as pd

from src.pipeline_01_config_setup_fun import read_params

logger = logging.getLogger(__name__)


def load_and_combine_data(config):
    """
    Load and combine SECOM sensor data with labels.
    """
    data_path = config["data_source"]["local_data_dir"]
    secom_path = os.path.join(data_path, "secom.data")
    labels_path = os.path.join(data_path, "secom_labels.data")

    if not os.path.exists(secom_path):
        raise FileNotFoundError(f"SECOM data file not found: {secom_path}")
    if not os.path.exists(labels_path):
        raise FileNotFoundError(f"SECOM labels file not found: {labels_path}")

    logger.info("Loading SECOM data from %s", data_path)
    df = pd.read_csv(secom_path, sep=r"\s+", header=None, na_values=["NaN", "nan"])
    labels_df = pd.read_csv(labels_path, sep=r"\s+", header=None, names=["Label", "Timestamp"])

    df.columns = [f"Sensor_{i}" for i in range(df.shape[1])]
    df["Output"] = labels_df["Label"]
    logger.info("Loaded %d samples × %d features", df.shape[0], df.shape[1] - 1)

    with open(os.path.join(config["artifacts_dir"]["general"], "Data_load_info.txt"), "w") as f:
        f.write("SECOM Dataset Loaded Successfully!\n")
        f.write(f"Feature Matrix Shape: {df.shape[0]} samples x {df.shape[1] - 1} features\n")
        f.write(f"Total Samples: {df.shape[0]}\n")
        f.write(f"Total Features (including Output): {df.shape[1]}\n")
        f.write("\nLabel Distribution:\n")
        f.write(df["Output"].value_counts().to_string() + "\n")
        f.write(f"\nFailure Rate: {100 * (df['Output'] == 1).sum() / len(df):.2f}%\n")

    return df


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s"
    )
    config_path = os.path.join("config", "params.yaml")
    config = read_params(config_path)
    artifacts_dir = config["artifacts_dir"]["general"]
    Path(artifacts_dir).mkdir(parents=True, exist_ok=True)
    df = load_and_combine_data(config)
    Path(raw_combined_data := config["data_source"]["raw_combined_data"]).mkdir(
        parents=True, exist_ok=True
    )
    df.to_csv(os.path.join(raw_combined_data, "combined_secom_data.csv"), index=False)
    logger.info("Data preparation completed.")
