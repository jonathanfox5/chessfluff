__author__ = "Jonathan Fox"
__copyright__ = "Copyright 2025, Jonathan Fox"
__license__ = "GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html"
__full_source_code__ = "https://github.com/jonathanfox5/chessfluff"

from chessfluff.config import Config
from chessfluff.logger import configure_logger
from chessfluff.requester import Requester

log = configure_logger()


class LichessAPI:
    """Class for querying the lichess.org public api"""

    def __init__(self, config: Config) -> None:
        """Class for querying the lichess.org public api

        Args:
            config (Config): Configuration data
        """
        self.requester = Requester(config)

        if not config.Api.lichess_key:
            log.warning("Lichess API key not set, requests may be slower")

        self.requester.set_header_parameter("Authorization", f"Bearer {config.Api.lichess_key}")

    def get_opening_stats(self, epd: str) -> dict:
        """Get the stats for a given position from the opening database (lichess games)

        Args:
            epd (str): EPD describing position

        Returns:
            dict: Stats for position
        """
        url = "https://explorer.lichess.ovh/lichess"
        params = {
            "variant": "standard",
            "fen": epd,
            "topGames": 0,
            "moves": 0,
            "recentGames": 0,
            "speeds": "blitz,rapid,classical",
            "ratings": "1200,1400,1600,1800,2000,2200,2500",
        }

        response = self.requester.get_json(url, params)

        return response

    def get_masters_stats(self, epd: str) -> dict:
        """Get the stats for a given position from the opening database (master games)

        Args:
            epd (str): EPD describing position

        Returns:
            dict: Stats for position
        """
        url = "https://explorer.lichess.ovh/masters"
        params = {
            "fen": epd,
            "topGames": 0,
            "moves": 0,
        }

        response = self.requester.get_json(url, params)

        return response
