__author__ = "Jonathan Fox"
__copyright__ = "Copyright 2025, Jonathan Fox"
__license__ = "GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html"
__full_source_code__ = "https://github.com/jonathanfox5/chessfluff"


import re
from pathlib import Path

import pandas as pd


def main() -> None:
    """Process lichess openings for use with chessfluff

    Instructions:

    1) Get the tsv files:
    git clone https://github.com/lichess-org/chess-openings
    cd chess-openings
    uv init
    uv add chess
    source .venv/bin/activate
    make
    deactivate

    2) Copy the generated tsvs to the same location as this script
    3) Run this script
    uv run resources/process_openings.py
    """

    print("Processing...")

    directory = "resources"
    output_file = "openings.tsv"

    # Can change this to a list of a.tsv, etc. if working with the individual files
    tsv_files = ["lichess_raw_openings.tsv"]

    df_list = [pd.read_csv(Path(directory, file), sep="\t") for file in tsv_files]
    df = pd.concat(df_list, ignore_index=True)

    df["family"] = df["name"].apply(lambda x: x.split(":")[0].split(",")[0])
    df["variation"] = df.apply(lambda x: get_variation(x["name"], x["family"]), axis=1)
    df["move_count"] = df["pgn"].apply(lambda x: count_moves(x))

    df = df[["eco", "family", "variation", "epd", "pgn", "move_count"]]

    print(f"Maximum move count = {df['move_count'].max()}")

    df.to_csv(Path(directory, output_file), sep="\t", index=False)

    print(f"Written to {Path(directory, output_file).absolute()}")


def get_variation(full_name: str, family: str) -> str:
    """Get the variation name given the full name and the family name

    Args:
        full_name (str): Full name of the opening
        family (str): Family name

    Returns:
        str: Variation name
    """

    # No variation present
    if full_name == family:
        return ""

    # Replace the version with family: variation
    result = full_name.replace(family + ": ", "")

    # Replace the version with family, variation
    result = result.replace(family + ", ", "")

    return result


def count_moves(clean_pgn: str) -> int:
    """Count the number of moves in a pgn

    Args:
        clean_pgn (str): Pgn stripped to move numbers and moves by python-chess

    Returns:
        int: Number of moves
    """
    move_no_pattern = r"[0-9][.]\s"

    moves = re.sub(move_no_pattern, "", clean_pgn)

    move_count = len(moves.split(" "))

    return move_count


if __name__ == "__main__":
    main()
