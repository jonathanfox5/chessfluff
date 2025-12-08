__author__ = "Jonathan Fox"
__copyright__ = "Copyright 2025, Jonathan Fox"
__license__ = "GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html"
__full_source_code__ = "https://github.com/jonathanfox5/chessfluff"


from pathlib import Path
from types import TracebackType
from typing import Self

import chess
import chess.engine


class Stockfish:
    """Run evaluations using stockfish"""

    def __init__(
        self, engine_path: Path, analysis_depth: int, threads: int, hash_size: int
    ) -> None:
        """Run evaluations using stockfish"""
        self.engine_path = str(engine_path.absolute())
        self.analysis_depth = analysis_depth
        self.threads = threads
        self.hash_size = hash_size

    def __enter__(self) -> Self:
        """Context manager for stockfish - entry

        Returns:
            Self: This class with active connection to Stockfish
        """

        self.engine = chess.engine.SimpleEngine.popen_uci(self.engine_path)

        self._configure_option("Threads", self.threads)
        self._configure_option("Hash", self.hash_size)

        self.engine.protocol

        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> bool | None:
        """Context manager for stockfish - exit

        Args:
            exc_type (type[BaseException] | None): Currently unused, part of standard definition of __exit__
            exc_value (BaseException | None): Currently unused, part of standard definition of __exit__
            traceback (TracebackType | None): Currently unused, part of standard definition of __exit__

        Returns:
            bool | None: Currently returns None, passing through all exceptions
        """
        self.engine.quit()
        return None

    def _configure_option(self, option_name: str, option_value: int) -> None:
        """Sets UCI options

        Args:
            option_name (str): Name of option, see https://official-stockfish.github.io/docs/stockfish-wiki/UCI-&-Commands.html#setoption
            option_value (int): Value to set option to, see https://official-stockfish.github.io/docs/stockfish-wiki/UCI-&-Commands.html#setoption
        """
        mapping = {option_name: option_value}
        self.engine.configure(mapping)

    def evaluate_position(self, epd: str) -> str | float:
        """Evaluates an EPD / FEN

        Args:
            epd (str): EPD or FEN describing board position

        Returns:
            str | float: One of "#x" (checkmate) "Mx" (mate in x) or x (eval in full pawns). Presence of a negative indicates black advantage.
        """
        board = chess.Board(epd)

        result_check = board.result()
        if result_check == "1-0":
            return "#0"
        if result_check == "0-1":
            return "#-0"

        response = self.engine.analyse(
            board, limit=chess.engine.Limit(nodes=self.analysis_depth), info=chess.engine.INFO_SCORE
        )

        pov_score: chess.engine.PovScore | None = response.get("score")

        if not pov_score:
            return 0.0

        white_score = pov_score.white()

        if white_score.is_mate():
            return f"M{white_score.mate()}"

        return float(white_score.score()) / 100.0  # type: ignore
