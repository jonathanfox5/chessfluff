__author__ = "Jonathan Fox"
__copyright__ = "Copyright 2025, Jonathan Fox"
__license__ = "GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html"
__full_source_code__ = "https://github.com/jonathanfox5/chessfluff"


import os
from json.decoder import JSONDecodeError

import httpx
from dotenv import load_dotenv

from chessfluff import __version__
from chessfluff.logger import configure_logger

log = configure_logger()


class Requester:
    """Wrapper for httpx module that retains data from previous run and configures
    headers to be compatible with chess.com's requirements"""

    def __init__(self, use_http2: bool = False):
        """Create new object with headers initialised from environment / .env file

        Args:
            use_http2 (bool, optional): True = http2, request as per chess.com's documentation,
                                        False = http1, seems to be faster.
                                        Defaults to False.
        """

        self._create_headers()
        self._client = httpx.Client(http2=use_http2, follow_redirects=True)

    def _create_headers(self):
        """Pulls data from environment / .env file to create user agent for request header"""

        load_dotenv()

        email = os.getenv("uaemail")
        username = os.getenv("uausername")
        app_name = __package__
        app_version = __version__

        user_agent = f"{app_name}/{app_version} (username: {username}; contact: {email})"

        self.request_headers = {"user-agent": user_agent}

    def get_json(self, url: str) -> dict:
        """Gets JSON data from an end point using a GET request

        Args:
            url (str): End point URL

        Returns:
            dict: json data converted to dict, empty dictionary returned on error
        """

        self.response_json = {}
        r = self._get(url=url)

        if r:
            try:
                self.response_json = r.json()
            except (httpx.DecodingError, JSONDecodeError) as exc:
                log.error(f"Could not decode JSON data for {url=}, {exc.args}")
                return {}

        return self.response_json

    def _get(self, url: str) -> httpx.Response | None:
        """Wrapper for httpx.get() with some error handling

        Args:
            url (str): End point URL

        Returns:
            httpx.Response | None: Returns the response object, otherwise None if error
        """

        self.success = False
        self.response_headers = {}
        self.request_url = url

        try:
            r = self._client.get(url=url, headers=self.request_headers)
        except httpx.RequestError as exc:
            log.error(f"An error occurred while requesting {exc.request.url!r}. {exc.args}")
            return None

        self.response_headers = dict(r.headers)
        self.status_code = r.status_code

        if r.status_code != httpx.codes.OK:
            log.error(f"Error {r.status_code}, {url=}")
            return None

        self.success = True

        return r
