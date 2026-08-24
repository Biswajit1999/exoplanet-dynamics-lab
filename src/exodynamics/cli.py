"""Command line interface."""

from __future__ import annotations

import argparse
import json

from exodynamics.pipeline import acquire_population, analyse_population, survey


def main() -> None:
    parser = argparse.ArgumentParser(prog="exodynamics")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("data", help="acquire timestamped NASA TAP snapshots")
    commands.add_parser("survey", help="acquire and analyse the live population")
    commands.add_parser("analyse", help="analyse already acquired snapshots")
    args = parser.parse_args()
    if args.command == "data":
        output: object = acquire_population()
    elif args.command == "survey":
        output = survey()
    else:
        output = analyse_population()
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()

