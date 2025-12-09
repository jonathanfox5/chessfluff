__author__ = "Jonathan Fox"
__copyright__ = "Copyright 2025, Jonathan Fox"
__license__ = "GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html"
__full_source_code__ = "https://github.com/jonathanfox5/chessfluff"


import io
from pathlib import Path

import chess.pgn
import pandas as pd


class OpeningDatabase:
    """Looks up opening data from the database"""

    def __init__(self, opening_database_path: Path) -> None:
        """Looks up opening data from the database

        Args:
            opening_database_path (Path): Path of opening database file
        """
        self._load_opening_database(opening_database_path)

    def _load_opening_database(self, opening_database_path: Path) -> None:
        """Read database in from tsv file

        Args:
            opening_database_path (Path): Path of opening database file
        """
        df = pd.read_csv(opening_database_path, sep="\t")
        df["variation"] = df["variation"].fillna("")
        self.opening_database = df

    def _load_pgn(self, pgn: str) -> chess.pgn.Game | None:
        """Create a game from a pgn

        Args:
            pgn (str): Game in pgn format

        Returns:
            chess.pgn.Game | None: Chess game
        """
        game = chess.pgn.read_game(io.StringIO(pgn))

        return game

    def get_opening(self, pgn: str, search_depth: int) -> list[dict]:
        """Get data about openings in a given game

        Args:
            pgn (str): Game in pgn format
            search_depth (int): Number of moves to check for named openings

        Returns:
            list[dict]: List of dictionaries containing opening data
        """
        blank_result = [
            {
                "eco": "X00",
                "family": "No opening",
                "variation": "",
                "full_name": "No opening",
                "epd": "",
                "pgn": "",
                "move_count": 0,
                "eval": 0,
                "master_games": 0,
                "master_white_win": 0.0,
                "master_black_win": 0.0,
                "master_draw": 0.0,
                "lichess_games": 0,
                "lichess_white_win": 0.0,
                "lichess_black_win": 0.0,
                "lichess_draw": 0.0,
            }
        ]

        game = self._load_pgn(pgn)

        if game is None:
            return blank_result

        board = game.board()

        move_count = 1
        openings = []
        for move in game.mainline_moves():
            if move_count >= search_depth:
                break

            board.push(move)
            epd = board.epd()
            opening = self.epd_to_opening(epd)

            if opening:
                openings.append(opening)

            move_count += 1

        if openings == []:
            return blank_result

        return openings

    def epd_to_opening(self, epd: str) -> dict | None:
        """Looks up a position in the database to find opening information

        Args:
            epd (str): Position in EPD format

        Returns:
            dict | None: Dictionary of opening data
        """
        df: pd.DataFrame = self.opening_database[self.opening_database["epd"] == epd]

        if df.shape[0] == 0:
            return None

        result = df.to_dict(orient="records")[0]

        return result
