import argparse

import geostats_datasets

parser = argparse.ArgumentParser(prog="python -m geostats_datasets")
commands = parser.add_subparsers(dest="command", required=True)
commands.add_parser("list", help="print the dataset names")
fetch = commands.add_parser("fetch", help="download a dataset and print its local path")
fetch.add_argument("name", help="dataset name, e.g. walker-lake")
fetch.add_argument("file", nargs="?", help="one file of the dataset, e.g. sample.csv")
args = parser.parse_args()

if args.command == "list":
    print("\n".join(geostats_datasets.list()))
else:
    print(geostats_datasets.fetch(args.name, args.file))
