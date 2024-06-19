"""
Functions for interacting with the 'database'    
"""

import csv
from pathlib import Path


def list_available_datasets():
    """docstring TODO"""
    return sorted(
        [
            path.name
            for path in list(Path("./database").glob("*"))
            if path.is_file() and not path.name.startswith(".")
        ]
    )


def get_dataset(dataset_name: str) -> list[dict]:
    """docstring TODO"""
    with open(f"database/{dataset_name}", "r", encoding="utf-8") as file:
        csv_reader = csv.DictReader(file)
        return list(csv_reader)
