import pandas as pd
from sklearn.preprocessing import StandardScaler
import joblib
from src.pipeline_01_config_setup_fun import read_params
import os

def feature_scaling(config):
    """
    Main function to standardize data.
    """
    print("Feature Standardization")
    print("=" * 50)
    df = pd.read_csv(
        os.path.join(config['data_preparation']['preprocessed_data_dir'], "preprocessed_secom_data.csv")
    )
    y = df['Output'].copy()
    df.drop('Output', axis=1, inplace=True)
    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(df)
    joblib.dump(scaler, os.path.join(config['artifacts_dir']['general'], "feature_scaler.pkl"))
    df_scaled = pd.DataFrame(scaled_features, columns=df.columns)
    print(f"Feature Standardization Completed. Scaled data shape: {df_scaled.shape}")
    df_scaled['Output'] = y
    df_scaled.to_csv(os.path.join(config['data_preparation']['preprocessed_data_dir'], "scaled_secom_data.csv"), index=False)
    return  

if __name__ == "__main__":
    config = read_params(os.path.join("config", "params.yaml"))
    feature_scaling(config)
    print("Feature Scaling Completed.")