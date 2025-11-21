"""
Main FPL Optimizer Script
Entry point for running optimization for each gameweek
"""

import argparse
import sys
import logging
from typing import Optional

from fpl_api import FPLAPIClient
from models import estimate_expected_points, HybridModel
from optimizer import FPLOptimizer
from cpv import CPVCalculator
from strategies import StrategyOverlay
from utils import (
    load_current_squad, save_gameweek_result, print_comparison_table,
    get_squad_player_ids, suggest_transfers, print_transfers,
    create_squad_template
)
from config import STARTING_11_BUDGET

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class FPLGameweekOptimizer:
    """Main orchestrator for FPL optimization"""

    def __init__(self, method: str = 'weighted_average',
                 robust: bool = False,
                 squad_constraint: bool = True,
                 strategy: str = 'standard'):
        """
        Initialize the gameweek optimizer

        Args:
            method: Prediction method to use
            robust: Whether to use robust optimization
            squad_constraint: Whether to constrain to current squad (vs optimize from all players)
            strategy: Strategic mode ('standard', 'rank_protection', 'rank_climbing')
        """
        self.method = method
        self.robust = robust
        self.squad_constraint = squad_constraint
        self.strategy = strategy
        self.api_client = FPLAPIClient()
        
    def optimize_gameweek(self, gameweek: Optional[int] = None) -> dict:
        """
        Run optimization for a specific gameweek
        
        Args:
            gameweek: Gameweek number (None = current gameweek)
            
        Returns:
            Dictionary with optimization results
        """
        # Get current gameweek if not specified
        if gameweek is None:
            gameweek = self.api_client.get_current_gameweek()
        
        logger.info(f"Optimizing for Gameweek {gameweek} using method: {self.method}")
        
        # Fetch player data
        logger.info("Fetching player data from FPL API...")
        players_df = self.api_client.get_all_players()
        
        # Calculate weeks remaining (assuming 38 gameweeks total)
        weeks_remaining = 38 - gameweek + 1
        
        # Get expected points based on method
        if self.method == 'hybrid':
            # Hybrid method requires fitting ML models
            logger.info("Using hybrid ML approach...")
            hybrid_model = HybridModel()
            hybrid_model.fit(players_df)
            expected_points_series = hybrid_model.hybrid_score(
                players_df, 
                players_df['total_points']
            )
            expected_points = expected_points_series.to_dict()
        else:
            # Other methods use historical data
            logger.info(f"Fetching player histories...")
            player_ids = players_df['id'].tolist()
            histories = self.api_client.get_player_histories_bulk(player_ids, gameweek)
            
            logger.info(f"Calculating expected points using {self.method}...")
            expected_points = estimate_expected_points(
                histories,
                method=self.method,
                weeks_to_end=weeks_remaining
            )

        # --- NEW: CPV CALCULATION ---
        logger.info("Calculating Composite Player Viability (CPV) scores...")

        # Get fixture difficulty for FFI calculation
        team_difficulty = self.api_client.get_next_fixture_difficulty(gameweek)

        # Calculate CPV
        cpv_calc = CPVCalculator(players_df, expected_points, team_difficulty)
        cpv_scores = cpv_calc.calculate_all()

        # --- NEW: STRATEGIC OVERLAY ---
        if self.strategy != 'standard':
            logger.info(f"Applying strategy: {self.strategy}")
            final_scores = StrategyOverlay.apply_strategy(cpv_scores, players_df, self.strategy)
        else:
            final_scores = cpv_scores

        # Add CPV scores to dataframe for display
        players_df['expected_points'] = players_df['id'].map(final_scores).fillna(0)

        # If squad constraint is enabled, filter to current squad
        if self.squad_constraint:
            squad_data = load_current_squad()
            squad_player_ids = get_squad_player_ids(squad_data, players_df)
            
            if squad_player_ids:
                logger.info(f"Constraining to current squad of {len(squad_player_ids)} players")
                players_df = players_df[players_df['id'].isin(squad_player_ids)]
            else:
                logger.warning("No squad found, optimizing from all players")
        
        # Run optimization
        logger.info("Running integer programming optimization on CPV scores...")
        optimizer = FPLOptimizer(
            players_df=players_df,
            expected_points=final_scores,
            budget=STARTING_11_BUDGET,
            robust=self.robust
        )
        
        solution = optimizer.solve()
        
        if solution is None:
            logger.error("Optimization failed!")
            return None
        
        # Print solution
        optimizer.print_solution()
        
        # Save results
        save_gameweek_result(
            gameweek=gameweek,
            method=self.method,
            starting_11=solution['selected_players'],
            captain_id=solution['captain_id'],
            expected_points=solution['expected_points']
        )
        
        return {
            'gameweek': gameweek,
            'method': self.method,
            'solution': solution,
            'optimizer': optimizer
        }
    
    def compare_methods(self, gameweek: Optional[int] = None) -> dict:
        """
        Compare all prediction methods
        
        Args:
            gameweek: Gameweek number (None = current gameweek)
            
        Returns:
            Dictionary with results from all methods
        """
        methods = [
            'simple_average',
            'weighted_average', 
            'exponential_smoothing',
            'monte_carlo',
            'arima',
            'linear_regression',
            'hybrid'
        ]
        
        results = {}
        
        for method in methods:
            logger.info(f"\n{'='*80}")
            logger.info(f"Testing method: {method}")
            logger.info(f"{'='*80}")

            optimizer = FPLGameweekOptimizer(
                method=method,
                squad_constraint=self.squad_constraint,
                strategy=self.strategy
            )
            try:
                result = optimizer.optimize_gameweek(gameweek)
                if result:
                    results[method] = {
                        'formation': result['solution']['formation'],
                        'expected_points': result['solution']['expected_points'],
                        'total_cost': result['solution']['total_cost'],
                        'captain_name': result['solution']['selected_players'][
                            result['solution']['selected_players']['is_captain']
                        ]['web_name'].values[0],
                        'full_result': result
                    }
            except Exception as e:
                logger.error(f"Method {method} failed: {e}")
                continue
        
        # Print comparison
        print_comparison_table(results)
        
        return results
    
    def suggest_transfers_for_optimal(self, gameweek: Optional[int] = None,
                                     max_transfers: int = 1):
        """
        Suggest transfers to move towards optimal team
        
        Args:
            gameweek: Gameweek number (None = current)
            max_transfers: Maximum number of transfers to suggest
        """
        # Get current squad
        squad_data = load_current_squad()
        
        # Get all players
        players_df = self.api_client.get_all_players()
        current_squad_ids = get_squad_player_ids(squad_data, players_df)
        
        if not current_squad_ids:
            print("No current squad found. Please set up your squad first.")
            return
        
        # Get optimal squad (without squad constraint)
        original_constraint = self.squad_constraint
        self.squad_constraint = False
        
        result = self.optimize_gameweek(gameweek)
        
        self.squad_constraint = original_constraint
        
        if result is None:
            return
        
        optimal_squad_ids = result['solution']['selected_players']['id'].tolist()
        
        # Get transfer suggestions
        transfers = suggest_transfers(
            current_squad_ids,
            optimal_squad_ids,
            players_df,
            max_transfers
        )
        
        print_transfers(transfers)


def main():
    """Main entry point with CLI"""
    parser = argparse.ArgumentParser(
        description='FPL Optimizer - Optimize your Fantasy Premier League team',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Optimize current gameweek with weighted average (recommended)
  python main.py --method weighted_average

  # Use Monte Carlo simulation
  python main.py --method monte_carlo

  # Use hybrid ML approach (highest peak performance)
  python main.py --method hybrid

  # Compare all methods
  python main.py --compare-all

  # Get transfer suggestions
  python main.py --suggest-transfers

  # Use robust optimization for risk-averse strategy
  python main.py --method weighted_average --robust

  # Use rank climbing strategy (find differentials to catch up)
  python main.py --method weighted_average --strategy rank_climbing

  # Use rank protection strategy (follow the crowd)
  python main.py --method weighted_average --strategy rank_protection

  # Optimize from ALL players (not just your squad)
  python main.py --method weighted_average --no-squad-constraint

  # Create squad template file
  python main.py --create-template
        """
    )
    
    parser.add_argument(
        '--method',
        type=str,
        default='weighted_average',
        choices=[
            'simple_average', 'weighted_average', 'exponential_smoothing',
            'monte_carlo', 'bootstrapping', 'arima', 'linear_regression', 'hybrid'
        ],
        help='Prediction method to use (default: weighted_average)'
    )
    
    parser.add_argument(
        '--gameweek',
        type=int,
        default=None,
        help='Specific gameweek to optimize (default: current gameweek)'
    )
    
    parser.add_argument(
        '--robust',
        action='store_true',
        help='Use robust optimization (worst-case scenario)'
    )

    parser.add_argument(
        '--strategy',
        type=str,
        default='standard',
        choices=['standard', 'rank_protection', 'rank_climbing'],
        help='Strategic mode: standard (max points), rank_protection (follow the crowd), rank_climbing (differentials)'
    )

    parser.add_argument(
        '--no-squad-constraint',
        action='store_true',
        help='Optimize from ALL players instead of current squad'
    )
    
    parser.add_argument(
        '--compare-all',
        action='store_true',
        help='Compare all prediction methods'
    )
    
    parser.add_argument(
        '--suggest-transfers',
        action='store_true',
        help='Suggest transfers to reach optimal squad'
    )
    
    parser.add_argument(
        '--max-transfers',
        type=int,
        default=1,
        help='Maximum number of transfers to suggest (default: 1)'
    )
    
    parser.add_argument(
        '--create-template',
        action='store_true',
        help='Create a squad template file'
    )
    
    args = parser.parse_args()
    
    # Handle create template
    if args.create_template:
        create_squad_template()
        return 0
    
    # Create optimizer
    optimizer = FPLGameweekOptimizer(
        method=args.method,
        robust=args.robust,
        squad_constraint=not args.no_squad_constraint,
        strategy=args.strategy
    )
    
    try:
        # Handle different modes
        if args.compare_all:
            optimizer.compare_methods(args.gameweek)
        elif args.suggest_transfers:
            optimizer.suggest_transfers_for_optimal(args.gameweek, args.max_transfers)
        else:
            optimizer.optimize_gameweek(args.gameweek)
        
        return 0
        
    except KeyboardInterrupt:
        logger.info("\nOptimization cancelled by user")
        return 1
    except Exception as e:
        logger.error(f"Error during optimization: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
