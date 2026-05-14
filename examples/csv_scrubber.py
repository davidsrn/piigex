# csv_scrubber.py: scrub specified columns in a CSV file.
#
# Usage:
#   cat data.csv | python examples/csv_scrubber.py --column email --column iban

import argparse
import csv
import sys

import piigex


def main() -> None:
    parser = argparse.ArgumentParser(description="Scrub PII from CSV columns.")
    parser.add_argument(
        "--column",
        action="append",
        dest="columns",
        metavar="NAME",
        default=[],
        help="Column name to scrub (repeatable).",
    )
    args = parser.parse_args()
    columns_to_scrub = set(args.columns)

    reader = csv.DictReader(sys.stdin)
    if reader.fieldnames is None:
        return

    writer = csv.DictWriter(sys.stdout, fieldnames=reader.fieldnames, lineterminator="\n")
    writer.writeheader()

    for row in reader:
        for col in columns_to_scrub:
            if col in row:
                row[col] = piigex.clean(row[col])
        writer.writerow(row)


if __name__ == "__main__":
    main()
