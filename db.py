"""
Functions for interacting with the 'database'    
"""

import csv
from pathlib import Path
import time


def list_available_datasets():
    """List datasets currently in the database"""
    time.sleep(2)  # simulate some waiting time
    return sorted(
        [
            path.name
            for path in list(Path("./database").glob("*"))
            if path.is_file() and not path.name.startswith(".")
        ]
    )


def get_dataset(dataset_name: str) -> list[dict]:
    """Fetches a dataset from the database"""
    time.sleep(2)  # simulate some waiting time
    with open(f"database/{dataset_name}", "r", encoding="utf-8") as file:
        csv_reader = csv.DictReader(file)
        type_map = {
            "dataset": str,
            "time": int,
            "group": str,
            "amount": int,
        }
        return [
            {colname: type_map[colname](value) for colname, value in row.items()}
            for row in csv_reader
        ]
