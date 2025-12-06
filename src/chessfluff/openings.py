__author__ = "Jonathan Fox"
__copyright__ = "Copyright 2025, Jonathan Fox"
__license__ = "GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html"
__full_source_code__ = "https://github.com/jonathanfox5/chessfluff"


import io
from pathlib import Path

import chess.pgn
import pandas as pd


class OpeningDatabase:
    opening_database: pd.DataFrame

    def __init__(self, opening_database_path: Path) -> None:
        self._load_opening_database(opening_database_path)

    def _load_opening_database(self, opening_database_path: Path) -> None:
        df = pd.read_csv(opening_database_path, sep="\t")
        df["variation"] = df["variation"].fillna("")
        self.opening_database = df

    def _load_pgn(self, pgn: str) -> chess.pgn.Game | None:
        game = chess.pgn.read_game(io.StringIO(pgn))

        return game

    def get_opening(self, pgn: str, search_depth: int) -> list[dict]:
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
        df: pd.DataFrame = self.opening_database[self.opening_database["epd"] == epd]

        if df.shape[0] == 0:
            return None

        result = df.to_dict(orient="records")[0]

        return result
