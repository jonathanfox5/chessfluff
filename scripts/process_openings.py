__author__ = "Jonathan Fox"
__copyright__ = "Copyright 2025, Jonathan Fox"
__license__ = "GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html"
__full_source_code__ = "https://github.com/jonathanfox5/chessfluff"


import re
import time
from pathlib import Path

import pandas as pd
from rich.progress import Progress, TaskID, track

from chessfluff.config import Config
from chessfluff.lichess_api import LichessAPI
from chessfluff.logger import configure_logger
from chessfluff.stockfish import Stockfish

log = configure_logger()


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

    log.info("Getting configuration information")
    config = Config()

    log.info("Manipulating lichess data")
    directory = config.Analysis.opening_database_path.parent
    output_file = config.Analysis.opening_database_path.name

    # You can change this to a list of a.tsv, etc. if working with the individual files
    tsv_files = ["lichess_raw_openings.tsv"]

    df_list = [pd.read_csv(directory / file, sep="\t") for file in tsv_files]
    df = pd.concat(df_list, ignore_index=True)

    df["family"] = df["name"].apply(lambda x: x.split(":")[0].split(",")[0])
    df["variation"] = df.apply(lambda x: get_variation(x["name"], x["family"]), axis=1)
    df["move_count"] = df["pgn"].apply(lambda x: count_moves(x))

    df = df[["eco", "family", "variation", "epd", "pgn", "move_count"]]
    log.info(f"Maximum moves for any = {df['move_count'].max()}")

    log.info("Calculating evals")
    sf = Stockfish(
        engine_path=config.Stockfish.path,
        analysis_depth=config.Stockfish.analysis_depth,
        threads=config.Stockfish.threads,
        hash_size=config.Stockfish.memory,
    )
    with Progress() as sf_progress:
        sf_task = sf_progress.add_task("Calculating eval using Stockfish", total=df.shape[0])

        with sf as sf_engine:
            df["eval"] = df.apply(
                lambda x: get_eval(sf_engine, sf_progress, sf_task, x["epd"]), axis=1
            )

    log.info("Getting lichess stats")
    lichess_stats = get_lichess_stats(df["epd"].to_list(), config)
    df = df.merge(right=lichess_stats, how="left", left_on="epd", right_on="epd")

    log.info("Writing data")
    df.to_csv(directory / output_file, sep="\t", index=False)
    log.info(f"Written to {Path(directory, output_file).absolute()}")


def get_lichess_stats(epds: list, config: Config) -> pd.DataFrame:
    api = LichessAPI(config)

    results = []
    for epd in track(epds, "Downloading lichess stats..."):
        # Query API, sleep for a second to avoid triggering rate limit
        time.sleep(1.001)
        master_stats = api.get_masters_stats(epd)
        time.sleep(1.001)
        lichess_game_stats = api.get_opening_stats(epd)

        master_white_games = master_stats.get("white", 0)
        master_black_games = master_stats.get("black", 0)
        master_draw_games = master_stats.get("draws", 0)
        master_total_games = master_white_games + master_black_games + master_draw_games

        lichess_white_games = lichess_game_stats.get("white", 0)
        lichess_black_games = lichess_game_stats.get("black", 0)
        lichess_draw_games = lichess_game_stats.get("draws", 0)
        lichess_total_games = lichess_white_games + lichess_black_games + lichess_draw_games

        result = {
            "epd": epd,
            "master_games": master_total_games,
            "master_white_win": calc_percentage(master_white_games, master_total_games),
            "master_black_win": calc_percentage(master_black_games, master_total_games),
            "master_draw": calc_percentage(master_draw_games, master_total_games),
            "lichess_games": lichess_total_games,
            "lichess_white_win": calc_percentage(lichess_white_games, lichess_total_games),
            "lichess_black_win": calc_percentage(lichess_black_games, lichess_total_games),
            "lichess_draw": calc_percentage(lichess_draw_games, lichess_total_games),
        }

        results.append(result)

    return pd.DataFrame(results)


def calc_percentage(numerator: int | float, denominator: int | float) -> float:
    try:
        result = numerator / denominator * 100.0
    except ZeroDivisionError:
        result = 0.0

    return result


def get_eval(sf: Stockfish, progress: Progress, task: TaskID, epd: str) -> str | float:
    result = sf.evaluate_position(epd)
    progress.update(task, advance=1)

    return result


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
