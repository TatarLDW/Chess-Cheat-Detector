"""
Configuration file - Single place to change settings
"""

from pathlib import Path

# ============================================
# USER CONFIGURATION - CHANGE THESE VALUES
# ============================================

# Player to analyze (change this to any username)
DEFAULT_PLAYER = "PLAYER_NAME"  # <-- CHANGE THIS

# PGN file to analyze
DEFAULT_PGN_FILE = "games.pgn"

# Stockfish engine path
STOCKFISH_PATH = "stockfish.exe"

# ============================================
# ADVANCED SETTINGS (Usually don't need to change)
# ============================================

# Analysis settings
MAX_GAMES = 500
ENGINE_ANALYSIS_TIME = 0.1  # seconds per move

# Output settings
OUTPUT_DIR = "reports"
CREATE_VIZ = True

# Helper functions
def get_player():
    """Get current player to analyze"""
    return DEFAULT_PLAYER

def get_pgn_file():
    """Get current PGN file to analyze"""
    return DEFAULT_PGN_FILE

def get_engine_path():
    """Get Stockfish engine path"""
    return STOCKFISH_PATH