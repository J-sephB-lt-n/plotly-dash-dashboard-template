"""
Functions for interacting with the 'database'    
"""

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
