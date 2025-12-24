import sys
import argparse
from scripts.load_initial_data import load_initial_data
from scripts.maintenance_script import run_maintenance


def main():
    parser = argparse.ArgumentParser(prog="agent-nexus")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("load-data")
    subparsers.add_parser("maintenance")

    args = parser.parse_args()

    if args.command == "load-data":
        load_initial_data()
    elif args.command == "maintenance":
        run_maintenance()
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
