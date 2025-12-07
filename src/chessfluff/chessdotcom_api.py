__author__ = "Jonathan Fox"
__copyright__ = "Copyright 2025, Jonathan Fox"
__license__ = "GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html"
__full_source_code__ = "https://github.com/jonathanfox5/chessfluff"

from chessfluff.config import Config
from chessfluff.requester import Requester


class ChessdotcomAPI:
    """Class for querying the chess.com public api"""

    def __init__(self, config: Config) -> None:
        """Class for querying the chess.com public api

        Args:
            config (Config): Configuration data
        """
        self.requester = Requester(config)

    def get_user_metadata(self, username: str) -> dict:
        """Gets metadata for a given user

        Args:
            username (str): Username to look up, must be lower case

        Returns:
            dict: Metadata for a given user
        """
        url = f"https://api.chess.com/pub/player/{username}"
        result = self._get_json(url)

        return result

    def get_user_stats(self, username: str) -> dict:
        """Gets statistics for a given user

        Args:
            username (str): Username to look up, must be lower case

        Returns:
            dict: Statistics for a given user
        """
        url = f"https://api.chess.com/pub/player/{username}/stats"
        result = self._get_json(url)

        return result

    def get_game_listing(self, username: str) -> dict:
        """Gets listing of end points to get monthly games for a given user

        Args:
            username (str): Username to look up, must be lower case

        Returns:
            dict: Contains end points for monthly data in {"archives": [...]}
        """
        url = f"https://api.chess.com/pub/player/{username}/games/archives"
        result = self._get_json(url)

        return result

    def get_all_games_in_month(self, username: str, year: int, month: int) -> dict:
        """Downloads games for a given user in a given month

        Args:
            username (str): Username to look up, must be lower case
            year (int): Year of interest
            month (int): Month of interest

        Returns:
            dict: Contains game data for a given month
        """
        url = f"https://api.chess.com/pub/player/{username}/games/{year}/{month:02}"
        result = self._get_json(url)

        return result

    def get_from_url(self, url: str) -> dict:
        """Downloads json from a given url.
        Used when travering a tree of data when a URL is given for the next endpoint.

        Args:
            url (str): Endpoint url

        Returns:
            dict: JSON data returned by endpoint
        """

        result = self._get_json(url)

        return result

    def get_country_data(self, country_code: str) -> dict:
        """Gets country data from API

        Args:
            country_code (str): Two letter ISO 3166-1 alpha-2 code

        Returns:
            dict: Country data
        """
        url = f"https://api.chess.com/pub/country/{country_code}"
        result = self._get_json(url)

        return result

    def user_exists(self, username: str) -> bool:
        """Checks if user exists

        Args:
            username (str): Username to look up, must be lower case

        Returns:
            bool: True if user exists
        """
        result = self.get_user_metadata(username) != {}
        return result

    def _get_json(self, url: str) -> dict:
        """Downloads json from a given url.
        Internal to class, used by other functions

        Args:
            url (str): Endpoint url

        Returns:
            dict: JSON data returned by endpoint
        """
        result = self.requester.get_json(url)
        return result
