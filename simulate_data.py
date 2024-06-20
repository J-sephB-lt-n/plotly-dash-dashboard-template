"""
Command-line script for simulating data

Example usage:
$ python simulate_data.py \
    --n_datasets 10 \
    --n_groups 3 \
    --n_rows_per_group 100 
"""

import argparse
import csv
import datetime
import random
import string
from dateutil.relativedelta import relativedelta
from pathlib import Path

arg_parser = argparse.ArgumentParser()
arg_parser.add_argument(
    "-d", "--n_datasets", help="Number of datasets to simulate", required=True, type=int
)
arg_parser.add_argument(
    "-g",
    "--n_groups",
    help="Number of simulated groups (per dataset)",
    required=True,
    type=int,
)
arg_parser.add_argument(
    "-r",
    "--n_rows_per_group",
    help="Number of rows (per group) in each dataset",
    required=True,
    type=int,
)
args = arg_parser.parse_args()

db_path = Path("./database")
files_to_delete = list(db_path.glob("*"))
if files_to_delete:
    print(f"Deleting {len(files_to_delete):,} file(s) from {db_path}..", end=" ")
    for file_path in files_to_delete:
        file_path.unlink()
    print("..done")

datasets = {}

datetime_now = datetime.datetime.now()
dataset_ids: list[str] = [
    (datetime_now + relativedelta(months=x)).strftime("%Y-%m")
    for x in range(args.n_datasets)
]
for dataset_id in dataset_ids:
    group_names: list[str] = [string.ascii_uppercase[i] for i in range(args.n_groups)]
    group_means: list[int] = [random.randint(10, 100) for _ in range(args.n_groups)]
    datasets[dataset_id] = []
    for group_name, group_mean in zip(group_names, group_means):
        for t in range(args.n_rows_per_group):
            datasets[dataset_id].append(
                {
                    "time": t,
                    "group": group_name,
                    "amount": int(random.gauss(group_mean, 20)),
                }
            )

for dataset_name, data in datasets.items():
    with open(f"./database/{dataset_name}.csv", mode="w", encoding="utf-8") as file:
        csv_writer = csv.DictWriter(
            file,
            fieldnames=["dataset", "time", "group", "amount"],
            delimiter=",",
            quotechar='"',
            quoting=csv.QUOTE_MINIMAL,
        )
        csv_writer.writeheader()
        for row in data:
            csv_writer.writerow({"dataset": dataset_name} | row)
