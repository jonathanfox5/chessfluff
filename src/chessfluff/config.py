__author__ = "Jonathan Fox"
__copyright__ = "Copyright 2025, Jonathan Fox"
__license__ = "GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html"
__full_source_code__ = "https://github.com/jonathanfox5/chessfluff"
__uses_code_from__ = {
    "https://github.com/jonathanfox5/gogadget/blob/main/src/gogadget/config.py": "AGPLv3+"
}

import tomllib
from dataclasses import dataclass
from pathlib import Path

from chessfluff import __version__


class Config:
    """Reads in configuration data from a toml file"""

    def __init__(self, config_path=Path("config.toml")) -> None:
        """Reads in configuration data from a toml file

        Args:
            config_path (Path, optional): Config file path. Defaults to Path("config.toml").

        Raises:
            FileNotFoundError: Can't find config file
            ValueError: Variable of unexpected type
            KeyError: Variable not found in config file
        """

        config_data = self._read_config_data(config_path)
        self._read_all_variables(config_data)

    def _read_config_data(self, config_path: Path) -> dict:
        """_summary_

        Args:
            config_path (Path): Path to config file

        Raises:
            FileNotFoundError: Can't find config file

        Returns:
            dict: Dictionary of Toml data
        """

        if not config_path.exists() or not config_path.is_file():
            raise FileNotFoundError(f"Could not find configuration file {config_path.absolute()}")

        with open("config.toml", "rb") as f:
            config_data = tomllib.load(f)

        return config_data

    def _read_all_variables(self, config_data: dict) -> None:
        """Reads all data from a toml dict into custom classes

        Args:
            config_data (dict): Dictionary of toml data

        Raises:
            ValueError: Variable of unexpected type
            KeyError: Variable not found in config file
        """

        self.Api.username = self._read_string(config_data, "api", "your_username")
        self.Api.email = self._read_string(config_data, "api", "your_email")

        self.Analysis.lookup_username = self._read_string(
            config_data, "analysis", "lookup_username"
        ).lower()
        self.Analysis.include_opponent_data = self._read_bool(
            config_data, "analysis", "include_opponent_data"
        )
        self.Analysis.analysis_period_months = self._read_int(
            config_data, "analysis", "analysis_period_months"
        )

    def _read_string(self, config_data: dict, category: str, variable_name: str) -> str:
        """Reads a string from loaded toml data

        Args:
            config_data (dict): Dictionary of toml data
            category (str): Toml category
            variable_name (str): Toml variable

        Raises:
            KeyError: Variable not found in config file

        Returns:
            str: Config value
        """
        result = str(config_data[category][variable_name]).strip()

        return result

    def _read_bool(self, config_data: dict, category: str, variable_name: str) -> bool:
        """Reads a boolean from loaded toml data

        Args:
            config_data (dict): Dictionary of toml data
            category (str): Toml category
            variable_name (str): Toml variable

        Raises:
            KeyError: Variable not found in config file
            ValueError: If data cannot be converted to a bool

        Returns:
            bool: Config value
        """
        value = config_data[category][variable_name]

        if isinstance(value, bool):
            return value

        if isinstance(value, str):
            value = value.lower().strip()

            if value == "true":
                return True
            elif value == "false":
                return False

        raise ValueError(f"Variable {category}{variable_name} is not a boolean (true / false)")

    def _read_int(self, config_data: dict, category: str, variable_name: str) -> int:
        """Reads an integer from loaded toml data

        Args:
            config_data (dict): Dictionary of toml data
            category (str): Toml category
            variable_name (str): Toml variable

        Raises:
            KeyError: Variable not found in config file
            ValueError: If data cannot be converted to an integer

        Returns:
            int: Config value
        """
        try:
            value = int(config_data[category][variable_name])
        except ValueError:
            raise ValueError(f"Variable {category}{variable_name} is not an integer")

        return value

    @dataclass
    class Api:
        """Stores user agent config data"""

        username = ""
        email = ""
        app_name = __package__
        app_version = __version__
        app_link = __full_source_code__

    @dataclass
    class Analysis:
        """Stores analysis config data"""

        lookup_username = ""
        include_opponent_data = True
        analysis_period_months = 9999
