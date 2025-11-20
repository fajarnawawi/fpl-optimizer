"""
Configuration settings for FPL Optimizer
Based on the paper: "Data-Driven Team Selection in Fantasy Premier League"
"""

# API Settings
FPL_API_BASE_URL = "https://fantasy.premierleague.com/api/"

# Budget Settings (in millions)
TOTAL_BUDGET = 100.0  # Total squad budget
STARTING_11_BUDGET = 100  # Budget for starting 11 (leaves 16.5M for reserves)
RESERVE_BUDGET = 0

# Formation Constraints
MIN_GOALKEEPERS = 1
MAX_GOALKEEPERS = 1
MIN_DEFENDERS = 3
MAX_DEFENDERS = 5
MIN_MIDFIELDERS = 3
MAX_MIDFIELDERS = 5
MIN_FORWARDS = 1
MAX_FORWARDS = 3

# Squad Constraints
SQUAD_SIZE = 15
STARTING_11_SIZE = 11
MAX_PLAYERS_PER_TEAM = 3

# Prediction Settings
MONTE_CARLO_SIMULATIONS = 1000
WEIGHTED_AVERAGE_RECENT_WEEKS = 5  # Focus on last 5 weeks for weighted average

# Robust Optimization Settings
DEFAULT_UNCERTAINTY_MARGIN = 0.2  # 15% uncertainty by default

# Hybrid Model Settings
HYBRID_ML_RATIO = (2, 1)  # (actual_points, predicted_points) ratio = 2:1
RIDGE_ALPHA = 1.0  # Regularization parameter

# Position Mappings
POSITION_MAP = {
    1: 'GKP',
    2: 'DEF',
    3: 'MID',
    4: 'FWD'
}

POSITION_REVERSE_MAP = {
    'GKP': 1,
    'GK': 1,
    'DEF': 2,
    'MID': 3,
    'FWD': 4,
    'FW': 4
}

# Scoring Features (for hybrid model)
# Features that contribute to points but aren't directly in the scoring system
SCORING_FEATURES = [
    'ict_index',
    'influence',
    'creativity',
    'threat',
    'expected_goals',
    'expected_assists',
    'expected_goal_involvements',
    'expected_goals_conceded',
    'starts'
]

# File Paths
SQUAD_FILE = 'data/my_squad.json'
HISTORY_FILE = 'data/player_history.json'
RESULTS_FILE = 'data/gameweek_results.json'

# Logging
LOG_LEVEL = 'INFO'
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
