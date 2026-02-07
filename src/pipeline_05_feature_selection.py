import os
import pandas as pd
from sklearn.feature_selection import mutual_info_classif
from src.pipeline_01_config_setup_fun import read_params


def feature_selection(config):
    """
    Main function to perform feature selection using mutual information.
    """
    print("Feature Selection using Mutual Information")
    print("=" * 50)
    df = pd.read_csv(
        os.path.join(config['data_preparation']['preprocessed_data_dir'], "scaled_secom_data.csv")
    )
    X = df.drop('Output', axis=1)
    y = df['Output']
    mi_scores = mutual_info_classif(X, y, random_state=config['base']['random_state'])
    mi_scores_series = pd.Series(mi_scores, index=X.columns).sort_values(ascending=False)
    selected_features = mi_scores_series[mi_scores_series > 0].index.tolist()
    print(f"Selected {len(selected_features)} features based on mutual information scores.")
    df_selected = df[selected_features + ['Output']]
    df_selected.to_csv(os.path.join(config['data_preparation']['preprocessed_data_dir'], "selected_features_secom_data.csv"), index=False)
    return selected_features

if __name__ == "__main__":
    config = read_params(os.path.join("config", "params.yaml"))
    selected_features = feature_selection(config)
    print("Feature Selection Completed.")
    print(f"Selected Features: {selected_features}")