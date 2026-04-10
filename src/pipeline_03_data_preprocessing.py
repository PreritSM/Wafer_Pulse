import logging
import os
import pandas as pd
from pathlib import Path

from sklearn.impute import SimpleImputer
from src.pipeline_01_config_setup_fun import read_params

logger = logging.getLogger(__name__)


def missing_value_imputation(df, config):
    """
    Imputes missing values in the dataframe using mean imputation.
    """
    logger.info("Starting mean imputation...")
    imputer = SimpleImputer(strategy='mean')
    missing_values_bfr_imputation = df.isnull().sum().sum()
    df_imputed = pd.DataFrame(imputer.fit_transform(df), columns=df.columns)
    missing_values_aft_imputation = df_imputed.isnull().sum().sum()
    logger.info("Mean imputation complete. Missing before=%d, after=%d",
                missing_values_bfr_imputation, missing_values_aft_imputation)
    with open(os.path.join(config['artifacts_dir']['general'],
                           "Missing_value_processing.txt"), 'a') as f:
        f.write("Handling Missing Values with Mean Imputation\n")
        f.write(f"Total Missing Values Before Imputation: {missing_values_bfr_imputation}\n")
        f.write(f"Total Missing Values After Imputation: {missing_values_aft_imputation}\n")
        f.write("Mean Imputation Completed Successfully!\n")

    return df_imputed


def missing_value_examination(config):
    """
    Examines missing values in the dataframe and returns a report.
    """
    csv_path = os.path.join(config['data_source']['raw_combined_data'], "combined_secom_data.csv")
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Raw combined data not found at: {csv_path}")

    logger.info("Examining missing values in %s", csv_path)
    df = pd.read_csv(csv_path)
    total_missing = df.isnull().sum().sum()
    total_cells = df.size
    missing_percentage = (total_missing / total_cells) * 100
    missing_per_column = df.isnull().sum()
    cols_with_missing = missing_per_column[missing_per_column > 0]

    with open(os.path.join(config['artifacts_dir']['general'],
                           'Missing_value_processing.txt'), 'w') as f:
        f.write(f"Total Missing Values: {total_missing} out of {total_cells} cells ({missing_percentage:.2f}%)\n")
        f.write(f"\nMissing Values per Column: {len(cols_with_missing)} columns with missing values\n")
        f.write(f"Columns without Missing Values: {df.shape[1] - len(cols_with_missing)} columns\n")
        f.write("Columns with Missing Values:\n")
        for col, missing_count in cols_with_missing.items():
            f.write(f"{col}: {missing_count} missing values\n")
        f.write("\n\n\n")

    y_labels = df['Output'].copy()
    df.drop('Output', axis=1, inplace=True)

    missing_threshold = config['data_preparation']['missing_threshold']
    missing_percentages = df.isnull().sum() / len(df)
    cols_to_drop = missing_percentages[missing_percentages > missing_threshold].index
    df.drop(cols_to_drop, axis=1, inplace=True)
    logger.info("Dropped %d columns exceeding %.0f%% missing threshold", len(cols_to_drop), missing_threshold * 100)

    with open(os.path.join(config['artifacts_dir']['general'], 'Missing_value_processing.txt'), 'a') as f:
        f.write(f"Columns with >{missing_threshold} missing values dropped: {len(cols_to_drop)}\n")

    return df, y_labels

def target_variable_encoding(y):
    """
    Encodes the target variable 'Output' to binary values.
    """
    y_encoded = y.map({-1: 0, 1: 1})
    return y_encoded

def data_preprocessing(config):
    """
    Main function to preprocess data.
    """
    df, y = missing_value_examination(config)
    logger.info("Missing value examination complete.")
    df_imputed = missing_value_imputation(df, config)
    logger.info("Missing value imputation complete.")
    y_encoded = target_variable_encoding(y)
    logger.info("Target variable encoding complete.")
    df_imputed['Output'] = y_encoded
    processed_data_dir = config['data_preparation']['preprocessed_data_dir']
    Path(processed_data_dir).mkdir(parents=True, exist_ok=True)
    df_imputed.to_csv(os.path.join(processed_data_dir, "preprocessed_secom_data.csv"), index=False)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    config_path = os.path.join("config", "params.yaml")
    config = read_params(config_path)
    data_preprocessing(config)
    logger.info("Data preprocessing completed.")