__author__ = "Jonathan Fox"
__copyright__ = "Copyright 2025, Jonathan Fox"
__license__ = "GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html"
__full_source_code__ = "https://github.com/jonathanfox5/chessfluff"


import datetime
from pathlib import Path

import pandas as pd
from rich.progress import track

from chessfluff.chessdotcom_api import ChessdotcomAPI
from chessfluff.config import Config
from chessfluff.logger import configure_logger
from chessfluff.mappings import game_result_lookup
from chessfluff.openings import OpeningDatabase
from chessfluff.utils import (
    iso_to_flag,
    json_to_file,
    username_from_profile_url,
)

log = configure_logger()


def main() -> None:
    """Main entry point"""

    _ = extract_data()


def extract_data() -> pd.DataFrame:
    """Extract user, oppoenent and game data from chess.com. Configured by settings in config.toml

    Returns:
        pd.DataFrame: Dataframe with combined data
    """

    log.info("Initialising data extraction")
    config = Config()
    api = ChessdotcomAPI(config)
    username = config.Analysis.lookup_username.lower()

    log.info(f"Getting data for player, {username}")
    players = [get_player_data(api, username)]
    if players == [{}]:
        log.critical(
            f"Could not load data for {username=}: does not exist or there is a network issue, cannot continue"
        )
        exit()

    raw_game_data = download_games(
        api=api, username=username, months_to_extract=config.Analysis.analysis_period_months
    )
    if raw_game_data == []:
        log.critical(f"No games found for {username=}, cannot continue")
        exit()

    games = process_games(
        username=username,
        games=raw_game_data,
        opening_search_depth=config.Analysis.opening_search_depth,
        opening_database_path=config.Analysis.opening_database_path,
    )

    if config.Analysis.include_opponent_data:
        players.extend(get_opponent_data(api, games))

    countries = get_country_data(api, players)

    log.info("Merging data")
    df_games = pd.DataFrame(games)
    df_players = pd.DataFrame(players)
    df_countries = pd.DataFrame(countries)
    df_combined = df_games.merge(
        right=df_players, how="left", left_on="opponent_name", right_on="formatted_username"
    )

    df_combined = df_combined.merge(
        right=df_countries, how="left", left_on="country_url", right_on="country_url"
    )

    # Writing data
    if config.Debug.write_json:
        log.info("Writing JSON files")
        json_to_file(players, "out_players.json")
        json_to_file(games, "out_games.json")
        json_to_file(countries, "out_countries.json")

    if config.Debug.write_dataframes:
        log.info("Writing dataframes to spreadsheets")
        df_games.to_excel("out_games.xlsx", index_label="index")
        df_players.to_excel("out_players.xlsx", index_label="index")
        df_countries.to_excel("out_countries.xlsx", index_label="index")
        df_combined.to_excel("out_combined.xlsx", index_label="index")

    return df_combined


def get_config_data(config_path=Path("config.toml")) -> Config:
    """Read configuration from a toml file

    Args:
        config_path (Path, optional): Path to toml file. Defaults to Path("config.toml").

    Returns:
        Config: Configuration data
    """

    log.info("Getting configuration data")

    try:
        config_path = Path("config.toml")
        config = Config(config_path)
    except FileNotFoundError as exc:
        log.critical(f"Config file cannot be read {config_path.absolute()}, cannot continue {exc}")
        exit()
    except (ValueError, KeyError) as exc:
        log.critical(
            f"Cannot read the section / variable from {config_path.absolute()}, cannot continue {exc}"
        )
        exit()

    return config


def get_player_data(api: ChessdotcomAPI, username: str) -> dict:
    """Gets selected metadata and stats for a given user

    Args:
        api (ChessAPI): API object to look up data
        username (str): Username to look up, must be lower case

    Returns:
        dict: Metadata and stats for a given user
    """
    player_metadata = api.get_user_metadata(username)
    player_stats = api.get_user_stats(username)

    if player_metadata == {} or player_stats == {}:
        return {}

    # Basic metadata
    formatted_username = username_from_profile_url(player_metadata.get("url", ""))
    if formatted_username == "":
        formatted_username = username

    player = {
        "username": username,
        "formatted_username": formatted_username,
        "country_url": player_metadata.get("country", "https://api.chess.com/pub/country/XX"),
        "player_status": player_metadata.get("status", "unknown"),
        "player_league": player_metadata.get("league", "unknown"),
        "is_streamer": player_metadata.get("is_streamer", False),
        "joined": datetime.datetime.fromtimestamp(player_metadata.get("joined", 0)),
        "fide_rating": player_stats.get("fide", 0),
    }

    # Results by game type
    game_types = ["rapid", "blitz", "bullet"]

    for game_type in game_types:
        player[f"{game_type}_rating"] = 0
        player[f"{game_type}_count"] = 0
        player[f"{game_type}_last_played"] = 0

        game_type_stats = player_stats.get(f"chess_{game_type}")
        if not game_type_stats:
            continue

        player[f"{game_type}_rating"] = game_type_stats["last"].get("rating", 0)
        player[f"{game_type}_count"] = (
            game_type_stats["record"].get("win", 0)
            + game_type_stats["record"].get("loss", 0)
            + game_type_stats["record"].get("draw", 0)
        )
        player[f"{game_type}_last_played"] = datetime.datetime.fromtimestamp(
            game_type_stats["last"]["date"]
        )

    return player


def get_opponent_data(api: ChessdotcomAPI, games: list) -> list:
    """Gets metadata / stats for opponents faced in a set of games

    Args:
        api (ChessAPI): API object to look up data
        games (list): Games to look up

    Returns:
        list: List of dictionaries containing user data
    """

    log.info("Getting unique list of opponents")
    usernames = []
    for game in games:
        username = game["opponent_name"].lower()

        if username not in usernames:
            usernames.append(username)

    log.info(f"Downloading data for {len(usernames)} opponents")
    players = []
    for username in track(usernames, "Downloading opponent data..."):
        player = get_player_data(api, username)

        if player != {}:
            players.append(player)

    return players


def get_country_data(api: ChessdotcomAPI, players: list) -> list:
    """Gets country data for a list of players

    Args:
        api (ChessAPI): API object to look up data
        players (list): Players to look up

    Returns:
        list: List of dictionaries containing country
    """

    log.info("Getting unique list of countries")
    country_urls = []
    for player in players:
        url = player["country_url"]

        if url not in country_urls:
            country_urls.append(url)

    log.info(f"Downloading data for {len(country_urls)} countries")
    countries = []
    for url in track(country_urls, "Downloading country data"):
        country_data = api.get_from_url(url)

        if country_data == {}:
            continue

        country_code = country_data.get("code", "Unknown")

        country = {
            "country_url": url,
            "country_code": country_code,
            "country_name": country_data.get("name", "Unknown"),
            "flag": iso_to_flag(country_code),
        }

        countries.append(country)

    return countries


def download_games(api: ChessdotcomAPI, username: str, months_to_extract: int) -> list:
    """Downloads all games of a given user

    Args:
        api (ChessAPI): API object to look up data
        username (str): Username to look up, must be lower case
        months_to_extract (int): Extract the x most recent months

    Returns:
        list: List of dictionaries containing game data
    """

    log.info("Downloading game listing")

    # Get listing of all games
    monthly_game_urls = api.get_game_listing(username).get("archives", [])

    log.info(f"{len(monthly_game_urls)} months of games available")

    if monthly_game_urls == []:
        return []

    monthly_game_urls = sorted(monthly_game_urls, reverse=True)
    monthly_game_urls = monthly_game_urls[:months_to_extract]

    log.info(
        f"Downloading {len(monthly_game_urls)} months of games, limit in config file = {months_to_extract}"
    )

    # Get games from monthly archives
    games = []
    for monthly_game_url in track(monthly_game_urls, "Downloading games..."):
        monthly_game = api.get_from_url(monthly_game_url)

        game_batch = monthly_game.get("games", [])
        if game_batch == []:
            log.warning(f"Could not read monthly games for {monthly_game_url=}")
        else:
            games.extend(game_batch)

    return games


def process_games(
    username: str, games: list, opening_search_depth: int, opening_database_path: Path
) -> list:
    """Extracts relevant data from unprocessed game data from Chess.com

    Args:
        username (str): Username of the main player, must be lower case
        games (list): List of games to process

    Returns:
        list: List of dictionaries of processed data
    """
    log.info("Loading opening database")
    opening_db = OpeningDatabase(opening_database_path)

    log.info(f"Processing {len(games)} games")

    processed_games = []
    for game in track(games, "Processing games..."):
        # Skip non-rated games
        if not game["rated"]:
            continue

        # Work out sides
        player_colour = "white"
        opponent_colour = "black"
        if game["black"]["username"].lower() == username:
            player_colour = "black"
            opponent_colour = "white"

        # Extract relevant data from json
        processed_game = {
            "game_url": game["url"],
            "pgn": game["pgn"],
            "time_control": game["time_control"],
            "end_time": datetime.datetime.fromtimestamp(game["end_time"]),
            "time_class": game["time_class"],
            "player_colour": player_colour,
            "opponent_colour": opponent_colour,
            "player_result": game[player_colour]["result"],
            "opponent_result": game[opponent_colour]["result"],
            "simple_result": game_result_lookup.get(game[player_colour]["result"], "Unknown"),
            "opponent_name": game[opponent_colour]["username"],
            "opponent_rating": game[opponent_colour]["rating"],
            "player_rating": game[player_colour]["rating"],
        }

        # Get opening information
        opening_list = opening_db.get_opening(game["pgn"], opening_search_depth)
        opening = opening_list[-1]

        processed_game["eco_code"] = opening["eco"]
        processed_game["opening_family"] = opening["family"]
        processed_game["opening_variation"] = opening["variation"]
        processed_game["opening_book_moves"] = opening["move_count"]
        processed_game["opening_eval"] = opening["eval"]
        processed_game["chess.com_opening"] = game["eco"]

        processed_games.append(processed_game)

    return processed_games
