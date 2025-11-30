__author__ = "Jonathan Fox"
__copyright__ = "Copyright 2025, Jonathan Fox"
__license__ = "GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html"
__full_source_code__ = "https://github.com/jonathanfox5/chessfluff"


# Map game result to score for win/loss/draw
game_scoring_lookup = {
    "win": 1.0,
    "checkmated": 0.0,
    "agreed": 0.5,
    "repetition": 0.5,
    "timeout": 0.0,
    "resigned": 0.0,
    "stalemate": 0.5,
    "lose": 0.0,
    "insufficient": 0.5,
    "50move": 0.5,
    "abandoned": 0.0,
    "kingofthehill": 0.0,
    "threecheck": 0.0,
    "timevsinsufficient": 0.5,
    "bughousepartnerlose": 0.0,
}

# Custom countries used by chess.com that don't conform to standard ISO codes
custom_country_codes = {
    "XA": "🇮🇨",  # Canary Islands
    "XB": "🇪🇸",  # Basque
    "XC": "🇪🇸",  # Catalonia
    "XE": "🏴󠁧󠁢󠁥󠁮󠁧󠁿",  # England
    "XG": "🇪🇸",  # Galicia
    "XK": "🇽🇰",  # Kosovo
    "XP": "🇵🇸",  # Palestine
    "XS": "🏴󠁧󠁢󠁳󠁣󠁴󠁿",  # Scotland
    "XW": "🏴󠁧󠁢󠁷󠁬󠁳󠁿",  # Wales
    "XX": "🏳️",  # International
}
