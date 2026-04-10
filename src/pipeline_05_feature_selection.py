import logging
import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.feature_selection import mutual_info_classif

from src.pipeline_01_config_setup_fun import read_params

logger = logging.getLogger(__name__)


def feature_selection(config):
    """
    Select top-N features using Mutual Information scores.
    """
    csv_path = os.path.join(
        config["data_preparation"]["preprocessed_data_dir"], "scaled_secom_data.csv"
    )
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Scaled data not found: {csv_path}")

    logger.info("Running Mutual Information feature selection on %s", csv_path)
    df = pd.read_csv(csv_path)
    y = df["Output"].copy()
    X = df.drop("Output", axis=1)

    mi_scores = mutual_info_classif(X, y, random_state=config["base"]["random_state"])
    mi_scores_series = pd.Series(mi_scores, index=X.columns).sort_values(ascending=False)
    top_n = config["data_preparation"]["top_n_features"]
    selected_features = mi_scores_series[:top_n].index.tolist()
    logger.info("Selected %d features out of %d", len(selected_features), X.shape[1])

    with open(
        os.path.join(config["artifacts_dir"]["general"], "feature_selection_report.txt"), "w"
    ) as f:
        f.write("Feature Selection Report\n")
        f.write("=" * 50 + "\n")
        f.write(f"Top {top_n} Features Selected:\n")
        for feature in selected_features:
            f.write(f"{feature}: MI Score = {mi_scores_series[feature]:.4f}\n")

    df_selected = df[selected_features + ["Output"]]
    os.makedirs(config["data_source"]["Train_Data_dir"], exist_ok=True)
    out_path = os.path.join(
        config["data_source"]["Train_Data_dir"], "selected_features_secom_data.csv"
    )
    df_selected.to_csv(out_path, index=False)
    logger.info("Selected feature data saved to %s", out_path)
    return selected_features, mi_scores_series


def visualize_feature_importance(mi_scores_series, config):
    """
    Visualizes feature importance based on mutual information scores.
    """
    # Create DataFrame for easier manipulation
    mi_df = pd.DataFrame(
        {"Feature": mi_scores_series.index, "MI_Score": mi_scores_series.values}
    ).sort_values("MI_Score", ascending=False)

    # Visualize Feature Importance
    fig, ax = plt.subplots(figsize=(12, 10))

    # Plot top 40 features
    top_40 = mi_df.head(40)
    colors = plt.cm.viridis(np.linspace(0.2, 0.8, 40))
    bars = ax.barh(range(len(top_40)), top_40["MI_Score"].values, color=colors)

    ax.set_yticks(range(len(top_40)))
    ax.set_yticklabels(top_40["Feature"].values)
    ax.invert_yaxis()
    ax.set_xlabel("Mutual Information Score", fontsize=12)
    ax.set_ylabel("Feature", fontsize=12)
    ax.set_title("Top 40 Features by Mutual Information Score", fontsize=14, fontweight="bold")

    # Add value labels
    for i, (bar, score) in enumerate(zip(bars, top_40["MI_Score"].values)):
        ax.text(
            score + 0.0002,
            bar.get_y() + bar.get_height() / 2,
            f"{score:.4f}",
            va="center",
            fontsize=8,
        )

    plt.tight_layout()
    plt.savefig(
        os.path.join(config["artifacts_dir"]["general"], "feature_importance.png"),
        dpi=300,
        bbox_inches="tight",
    )
    plt.close()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s"
    )
    config = read_params(os.path.join("config", "params.yaml"))
    selected_features, mi_scores_series = feature_selection(config)
    logger.info("Feature selection completed. Selected: %s", selected_features)
    visualize_feature_importance(mi_scores_series, config)
