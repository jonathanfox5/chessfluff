__author__ = "Jonathan Fox"
__copyright__ = "Copyright 2025, Jonathan Fox"
__license__ = "GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html"
__full_source_code__ = "https://github.com/jonathanfox5/chessfluff"


import logging

from rich.logging import RichHandler


def configure_logger(
    global_level: int = logging.WARNING,
    package_level: int = logging.DEBUG,
) -> logging.Logger:
    """Configure a python logger to use Rich

    Args:
        global_level (int, optional): Logging level for all dependencies. Defaults to logging.ERROR.
        package_level (int, optional): Logging level for application specific code. Defaults to logging.DEBUG.

    Returns:
        logging.Logger: Configured Logger object
    """

    # Global settings
    logging.basicConfig(
        level=global_level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(rich_tracebacks=True)],
    )

    # Our handler for our package
    log = logging.getLogger(__package__)
    log.setLevel(package_level)

    return log
