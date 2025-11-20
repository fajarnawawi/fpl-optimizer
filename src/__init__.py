"""
FPL Optimizer Package
Based on the paper: "Data-Driven Team Selection in Fantasy Premier League"
"""

__version__ = "1.0.0"
__author__ = "Based on research by Danial Ramezani"

from .fpl_api import FPLAPIClient
from .models import PredictionModels, HybridModel, estimate_expected_points
from .optimizer import FPLOptimizer
from .utils import (
    load_current_squad,
    save_current_squad,
    save_gameweek_result,
    suggest_transfers,
    print_transfers,
    create_squad_template
)

__all__ = [
    'FPLAPIClient',
    'PredictionModels',
    'HybridModel',
    'estimate_expected_points',
    'FPLOptimizer',
    'load_current_squad',
    'save_current_squad',
    'save_gameweek_result',
    'suggest_transfers',
    'print_transfers',
    'create_squad_template'
]
