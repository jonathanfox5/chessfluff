__author__ = "Jonathan Fox"
__copyright__ = "Copyright 2025, Jonathan Fox"
__license__ = "GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html"
__full_source_code__ = "https://github.com/jonathanfox5/chessfluff"


import json
from pathlib import Path

from chessfluff.logger import configure_logger
from chessfluff.mappings import custom_country_codes

log = configure_logger()


def json_to_file(data: dict | list, filename: str, indent: int | None = 2) -> None:
    """Write a dictionary as a json to a file

    Args:
        filename (str): Name of file
        data (dict): Data to write
        indent (int | None, optional): Setting to None write without formatting, int>=0 formats with given number of indents. Defaults to 2.
    """
    path = Path(filename)
    with path.open("w") as f:
        json.dump(data, f, indent=indent, default=str)


def iso_to_flag(iso_code: str) -> str:
    """Get flag emoji for a given ISO code with support for user defined codes from chess.com

    Args:
        iso_code (str): Two letter ISO 3166-1 alpha-2 code

    Returns:
        str: Flag character
    """

    if len(iso_code) != 2:
        log.warning(f"Country code {iso_code} invalid, needs to be 2 characters long")

    iso_code = iso_code.upper()

    flag = ""
    if iso_code[0] != "X":
        # Standard codes
        flag = chr(ord(iso_code[0]) + 127397) + chr(ord(iso_code[1]) + 127397)
    else:
        # Map using Chess.com custom codes
        flag = custom_country_codes.get(iso_code, "🏳️")

    return flag


def username_from_profile_url(url: str) -> str:
    """Get user name from the url of a chess.com profile page

    Args:
        url (str): Chess.com profile page url

    Returns:
        str: Chess.com username
    """

    username = url.rsplit("/", 1)[-1]

    return username
