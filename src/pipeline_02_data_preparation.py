import os
import pandas as pd
from pathlib import Path
from src.pipeline_01_config_setup_fun import read_params

def load_and_combine_data(config):
    """
    Main function to prepare (load and combine) data based on the Secco.Data
    """
    DATA_PATH = config['data_source']['local_data_dir']
    df = pd.read_csv(
    os.path.join(DATA_PATH, "secom.data"),
    sep=r'\s+',
    header=None,
    na_values=['NaN', 'nan']
    )

    labels_df = pd.read_csv(
    os.path.join(DATA_PATH, "secom_labels.data"),
    sep=r'\s+',
    header=None,
    names=['Label', 'Timestamp']
    )

    # Assign column names to features (Sensor_0, Sensor_1, ..., Sensor_590)
    df.columns = [f'Sensor_{i}' for i in range(df.shape[1])]

    # Add labels to the dataframe
    df['Output'] = labels_df['Label']

    with open(os.path.join(config['artifacts_dir']['general'], 
                           f'Data_load_info.txt'),
                             'w') as f:
        f.write("✅ SECOM Dataset Loaded Successfully!\n")
        f.write(f"Feature Matrix Shape: {df.shape[0]} samples × {df.shape[1]-1} features\n")
        f.write(f"Total Samples: {df.shape[0]}\n")
        f.write(f"Total Features (including Output): {df.shape[1]}\n")
        f.write("\nLabel Distribution:\n")
        f.write(df['Output'].value_counts().to_string() + "\n")
        f.write(f"\nFailure Rate: {100 * (df['Output'] == 1).sum() / len(df):.2f}%\n")
    f.close()
    return df


if __name__ == "__main__":
    config_path = os.path.join("config", "params.yaml")
    config = read_params(config_path)
    artifacts_dir = config['artifacts_dir']['general']
    Path(artifacts_dir).mkdir(parents=True, exist_ok=True)
    df = load_and_combine_data(config)
    Path(raw_combined_data := config['data_source']['raw_combined_data']).mkdir(parents=True, exist_ok=True)
    df.to_csv(os.path.join(raw_combined_data, "combined_secom_data.csv"), index=False)