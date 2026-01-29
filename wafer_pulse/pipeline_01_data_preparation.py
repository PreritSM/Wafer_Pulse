import os
from pathlib import Path
import argparse
import yaml
import logging


if __name__ == "__main__":
    args = argparse.ArgumentParser()
    args.add_argument(
        "--config",
        type=str,
        default="default.yaml",
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