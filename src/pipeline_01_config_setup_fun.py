import os
from pathlib import Path
import argparse
import yaml
import logging

def read_params(config_path):
    """
    Reads a YAML configuration file and returns the parameters as a dictionary.
    """
    with open(config_path, 'r') as file:
        params = yaml.safe_load(file)
    return params

def main(config_path,datasource_path):
    """
    Main function to prepare data based on the configuration file and data source path.
    """
    config = read_params(config_path)
    print(f"Configuration parameters: {config}")


if __name__ == "__main__":
    args = argparse.ArgumentParser()
    default_config_path=os.path.join("config", "params.yaml")
    args.add_argument(
        "--config",
        type=str,
        
        default=default_config_path,
        help="Path to the configuration file.",
    )
    args.add_argument(
        "--datasource",
        type=str,
        default=None,
        help="Path to the data source directory."
    )

    parsed_args = args.parse_args()
    print(f"Parsed arguments: {parsed_args}")
    main(config_path=parsed_args.config, datasource_path=parsed_args.datasource)