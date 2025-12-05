__author__ = "Jonathan Fox"
__copyright__ = "Copyright 2025, Jonathan Fox"
__license__ = "GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html"
__full_source_code__ = "https://github.com/jonathanfox5/chessfluff"


# Map game result to score for win/loss/draw
game_result_lookup = {
    "win": "win",
    "checkmated": "loss",
    "agreed": "draw",
    "repetition": "draw",
    "timeout": "loss",
    "resigned": "loss",
    "stalemate": "draw",
    "lose": "loss",
    "insufficient": "draw",
    "50move": "draw",
    "abandoned": "loss",
    "kingofthehill": "loss",
    "threecheck": "loss",
    "timevsinsufficient": "draw",
    "bughousepartnerlose": "loss",
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
