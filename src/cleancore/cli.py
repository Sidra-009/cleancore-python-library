"""cli.py -- Minimal command-line interface for CleanCore."""

from __future__ import annotations

import argparse
import json

from . import __version__


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="cleancore",
        description="CleanCore -- Data Observability CLI",
    )
    parser.add_argument("--version", action="version", version=f"cleancore {__version__}")
    parser.add_argument("--report", metavar="FILE", help="Pretty-print an audit JSON file")
    args = parser.parse_args()

    if args.report:
        with open(args.report, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        print(json.dumps(data, indent=2))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
