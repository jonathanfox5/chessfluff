__author__ = "Jonathan Fox"
__copyright__ = "Copyright 2025, Jonathan Fox"
__license__ = "GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html"
__full_source_code__ = "https://github.com/jonathanfox5/chessfluff"


import time
from json.decoder import JSONDecodeError

import httpx

from chessfluff.config import Config
from chessfluff.logger import configure_logger

log = configure_logger()


class Requester:
    """Wrapper for httpx module that retains data from previous run and configures
    headers to be compatible with chess.com's requirements"""

    def __init__(
        self,
        config: Config.Api,
    ) -> None:
        """Create new object with headers initialised from environment / .env file

        Args:
            api_config (Config.Api): Api configuration data
        """

        self.request_headers = {}
        self._set_user_agent(config)

        self._client = httpx.Client(
            http2=config.use_http2, follow_redirects=config.follow_redirects
        )

        self.rate_limit_attempts = config.rate_limit_attempts
        self.rate_limit_timeout = config.rate_limit_timeout

        self.rate_limited = False
        self.rate_limit_last_timestamp = 0.0

    def set_header_parameter(self, parameter: str, value: str) -> None:
        self.request_headers[parameter] = value

    def _set_user_agent(self, config: Config.Api) -> None:
        """Uses information from config object to create user agent for request header

        Args:
            config (Config.Api): Configuration data
        """

        user_agent = f"{config.app_name}/{config.app_version} (username: {config.username}; contact: {config.email}, url: {config.app_link})"

        self.set_header_parameter("user-agent", user_agent)

    def get_json(self, url: str, query_params: dict | None = None) -> dict:
        """Gets JSON data from an end point using a GET request

        Args:
            url (str): End point URL
            query_params (dict | None): Query parameters for the get request. Defaults to None

        Returns:
            dict: json data converted to dict, empty dictionary returned on error
        """

        self.response_json = {}
        r = self._get(url=url, query_params=query_params)

        if r:
            try:
                self.response_json = r.json()
            except (httpx.DecodingError, JSONDecodeError) as exc:
                log.error(f"Could not decode JSON data for {url=}, {exc.args}")
                return {}

        return self.response_json

    def _get(self, url: str, query_params: dict | None = None) -> httpx.Response | None:
        """Wrapper for httpx.get() with some error handling

        Args:
            url (str): End point URL
            query_params (dict | None): Query parameters for the get request. Defaults to None

        Returns:
            httpx.Response | None: Returns the response object, otherwise None if error
        """

        self.success = False
        self.response_headers = {}
        self.request_url = url

        for _ in range(0, self.rate_limit_attempts):
            self._wait_rate_limit_timeout()

            try:
                r = self._client.get(url=url, headers=self.request_headers, params=query_params)
            except httpx.RequestError as exc:
                log.error(f"An error occurred while requesting {exc.request.url!r}. {exc.args}")
                return None

            if r.status_code == httpx.codes.TOO_MANY_REQUESTS:
                self._set_rate_limit_timeout()
            else:
                break

        self.response_headers = dict(r.headers)
        self.status_code = r.status_code

        if r.status_code != httpx.codes.OK:
            log.error(f"Error {r.status_code}, {url=}")
            return None

        self.success = True

        return r

    def _wait_rate_limit_timeout(self) -> None:
        if not self.rate_limited:
            return None

        current_time = time.time()

        wait_time = self.rate_limit_timeout - (current_time - self.rate_limit_last_timestamp)

        if wait_time > 0:
            log.info(f"Rate limit reached, code 429 received. Waiting {wait_time} seconds")
            time.sleep(wait_time)

        self.rate_limited = False

    def _set_rate_limit_timeout(self) -> None:
        log.info("Rate limit reached, code 429 received. Timeout will be applied to next request")
        self.rate_limited = True
        self.rate_limit_last_timestamp = time.time()
