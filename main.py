import argparse
import asyncio
import json
import sys
from pathlib import Path

from core.data_extractor import get_sorted_data
from core.parse_data import async_version
from core.utils import colorize_text


def main():
    """
    Compare packages between two branches and optionally save results to a file or print them to the console.

    This script uses command line arguments to specify two branches to compare. It retrieves packet data asynchronously,
    compares them, and outputs the results. If the `--write` argument is specified, the results
    saved to a JSON file with a name derived from the branch names. If the `--console` argument is specified,
    the results will be output to the console.

    Command-line Arguments:
        --branch1 (str): The name of the first branch to compare.
        --branch2 (str): The name of the second branch to compare.
        --write (str, optional): The directory path where the output JSON file will be saved. If not provided, the
                                  results will only be printed to stdout.
        --console (bool, optional): Print the results to stdout in JSON format if this flag is provided.

    Behavior:
        1. Parses command-line arguments to get branch names and output file path.
        2. Fetches package data for the specified branches asynchronously using `async_version`.
        3. Compares the package data and generates a result using `get_sorted_data`.
        4. If the `--write` argument is provided, writes the results to a JSON file in the specified directory.
        5. If the `--console` argument is provided, prints the results in JSON format to the console. By default,
           results are not printed unless this flag is specified.

    Examples:
        $ python script.py --branch1 branch1_name --branch2 branch2_name --write /path/to/output
        $ python script.py --branch1 branch1_name --branch2 branch2_name --console
    """
    parser = argparse.ArgumentParser(description="Compare packages between two branches.")
    parser.add_argument(
        "--branch1",
        required=True,
        help="Name of the first branch"
    )
    parser.add_argument(
        "--branch2",
        required=True,
        help="Name of the second branch, " "the branch in which we will search for newer versions",
    )
    parser.add_argument(
        "--write",
        help="Path to the output file, will be written " "to the file branch1-branch2.json",
    )
    parser.add_argument(
        "--console",
        action="store_true",
        help="Output the result to the stdout",
    )

    args = parser.parse_args()

    sys.stdout.write(f"\n{colorize_text(color='green', text="Hey, I'm starting work.")}" + "\n")
    sys.stdout.write(
        f"\n\tI'm starting work on two branches: "
        f"{colorize_text('green', args.branch1)} "
        f"and "
        f"{colorize_text('green', args.branch2)}." + "\n"
    )

    sys.stdout.write("\n\tSending requests to the API\n")
    received_data = asyncio.run(async_version(args.branch1, args.branch2))
    sys.stdout.write("\tData successfully received\n")

    sys.stdout.write("\n\tI'm starting to work with the data\n")
    result = get_sorted_data(received_data[0], received_data[1])
    sys.stdout.write("\tEverything went well, the data is sorted\n")

    if args.write is not None:
        path = Path(args.write) / f"{args.branch1}-{args.branch2}.json"
        with open(path, "w") as file:
            json.dump(result, file, indent=4)
        sys.stdout.write(
            f"\n\t{
        colorize_text(
            'green',
            'The result of the calculations is written to a file at the path: ')}"
            f"{colorize_text('purple', str(path))}\n"
        )

    if args.console:
        formatted_json = json.dumps(result, indent=4, ensure_ascii=False)
        sys.stdout.write(formatted_json + "\n")

    sys.stdout.write(
        f"\n{
    colorize_text(
        'green',
        'The results will be available according to your settings')}\n"
    )
