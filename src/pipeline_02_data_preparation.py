import os
import pandas as pd
from pathlib import Path
from src.pipeline_01_config_setup_fun import read_params

def main(config):
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

    with open(os.path.join(config['data_source']['artifacts_dir'], 
                           f'Data_load_info.txt'),
                             'w') as f:
        f.write("✅ SECOM Dataset Loaded Successfully!\n")
        f.write(f"Total Samples: {df.shape[0]}\n")
        f.write(f"Total Features (including Output): {df.shape[1]}\n")
        f.write("\nLabel Distribution:\n")
        f.write(df['Output'].value_counts().to_string() + "\n")
        f.write(f"\nFailure Rate: {100 * (df['Output'] == 1).sum() / len(df):.2f}%\n")


if __name__ == "__main__":
    config_path = os.path.join("config", "params.yaml")
    config = read_params(config_path)
    artifacts_dir = config['data_source']['artifacts_dir']
    Path(artifacts_dir).mkdir(parents=True, exist_ok=True)
    main(config)