"""
Integer Programming Optimizer for FPL Team Selection
Based on the paper's mathematical formulation
"""

import pulp
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
import logging

from config import (
    STARTING_11_BUDGET,
    STARTING_11_SIZE,
    MIN_GOALKEEPERS, MAX_GOALKEEPERS,
    MIN_DEFENDERS, MAX_DEFENDERS,
    MIN_MIDFIELDERS, MAX_MIDFIELDERS,
    MIN_FORWARDS, MAX_FORWARDS,
    MAX_PLAYERS_PER_TEAM,
    DEFAULT_UNCERTAINTY_MARGIN
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FPLOptimizer:
    """
    Integer Programming optimizer for FPL team selection
    Implements the model from the paper with both deterministic and robust formulations
    """
    
    def __init__(self, players_df: pd.DataFrame, 
                 expected_points: Dict[int, float],
                 budget: float = STARTING_11_BUDGET,
                 robust: bool = False,
                 uncertainty_margin: float = DEFAULT_UNCERTAINTY_MARGIN):
        """
        Initialize optimizer
        
        Args:
            players_df: DataFrame with all available players
            expected_points: Dict mapping player_id to expected points
            budget: Available budget for starting 11
            robust: Whether to use robust optimization
            uncertainty_margin: Uncertainty margin for robust optimization (e.g., 0.15 = 15%)
        """
        self.players_df = players_df.copy()
        self.expected_points = expected_points
        self.budget = budget
        self.robust = robust
        self.uncertainty_margin = uncertainty_margin
        
        # Add expected points to dataframe
        self.players_df['expected_points'] = self.players_df['id'].map(expected_points).fillna(0)
        
        # Calculate uncertainty bounds for robust optimization
        if robust:
            self.players_df['points_lower'] = self.players_df['expected_points'] * (1 - uncertainty_margin)
            self.players_df['points_upper'] = self.players_df['expected_points'] * (1 + uncertainty_margin)
        
        self.problem = None
        self.player_vars = {}
        self.captain_vars = {}
        self.solution = None
        
    def build_model(self):
        """Build the integer programming model"""
        
        # Create the optimization problem (Maximization)
        self.problem = pulp.LpProblem("FPL_Team_Selection", pulp.LpMaximize)
        
        # Decision variables
        # x[i] = 1 if player i is selected, 0 otherwise
        self.player_vars = {
            row['id']: pulp.LpVariable(f"player_{row['id']}", cat='Binary')
            for _, row in self.players_df.iterrows()
        }
        
        # y[i] = 1 if player i is captain, 0 otherwise
        self.captain_vars = {
            row['id']: pulp.LpVariable(f"captain_{row['id']}", cat='Binary')
            for _, row in self.players_df.iterrows()
        }
        
        # Objective function: Maximize expected points (including captain bonus)
        if self.robust:
            # Robust: maximize worst-case points
            objective = pulp.lpSum([
                self.players_df.loc[self.players_df['id'] == pid, 'points_lower'].values[0] * 
                (self.player_vars[pid] + self.captain_vars[pid])
                for pid in self.player_vars
            ])
        else:
            # Deterministic: maximize expected points
            objective = pulp.lpSum([
                self.players_df.loc[self.players_df['id'] == pid, 'expected_points'].values[0] * 
                (self.player_vars[pid] + self.captain_vars[pid])
                for pid in self.player_vars
            ])
        
        self.problem += objective, "Total_Expected_Points"
        
        # Constraint 1: Select exactly 11 players
        self.problem += (
            pulp.lpSum([self.player_vars[pid] for pid in self.player_vars]) == STARTING_11_SIZE,
            "Exactly_11_Players"
        )
        
        # Constraint 2: Budget constraint
        self.problem += (
            pulp.lpSum([
                self.players_df.loc[self.players_df['id'] == pid, 'cost'].values[0] * 
                self.player_vars[pid]
                for pid in self.player_vars
            ]) <= self.budget,
            "Budget_Constraint"
        )
        
        # Constraint 3: Exactly one captain
        self.problem += (
            pulp.lpSum([self.captain_vars[pid] for pid in self.captain_vars]) == 1,
            "Exactly_One_Captain"
        )
        
        # Constraint 4: Captain must be a selected player
        for pid in self.player_vars:
            self.problem += (
                self.captain_vars[pid] <= self.player_vars[pid],
                f"Captain_Must_Be_Selected_{pid}"
            )
        
        # Constraint 5: Formation constraints
        # Goalkeepers
        gk_players = self.players_df[self.players_df['position'] == 'GKP']['id'].tolist()
        self.problem += (
            pulp.lpSum([self.player_vars[pid] for pid in gk_players]) >= MIN_GOALKEEPERS,
            "Min_Goalkeepers"
        )
        self.problem += (
            pulp.lpSum([self.player_vars[pid] for pid in gk_players]) <= MAX_GOALKEEPERS,
            "Max_Goalkeepers"
        )
        
        # Defenders
        def_players = self.players_df[self.players_df['position'] == 'DEF']['id'].tolist()
        self.problem += (
            pulp.lpSum([self.player_vars[pid] for pid in def_players]) >= MIN_DEFENDERS,
            "Min_Defenders"
        )
        self.problem += (
            pulp.lpSum([self.player_vars[pid] for pid in def_players]) <= MAX_DEFENDERS,
            "Max_Defenders"
        )
        
        # Midfielders
        mid_players = self.players_df[self.players_df['position'] == 'MID']['id'].tolist()
        self.problem += (
            pulp.lpSum([self.player_vars[pid] for pid in mid_players]) >= MIN_MIDFIELDERS,
            "Min_Midfielders"
        )
        self.problem += (
            pulp.lpSum([self.player_vars[pid] for pid in mid_players]) <= MAX_MIDFIELDERS,
            "Max_Midfielders"
        )
        
        # Forwards
        fwd_players = self.players_df[self.players_df['position'] == 'FWD']['id'].tolist()
        self.problem += (
            pulp.lpSum([self.player_vars[pid] for pid in fwd_players]) >= MIN_FORWARDS,
            "Min_Forwards"
        )
        self.problem += (
            pulp.lpSum([self.player_vars[pid] for pid in fwd_players]) <= MAX_FORWARDS,
            "Max_Forwards"
        )
        
        # Constraint 6: Max 3 players per team
        for team_id in self.players_df['team'].unique():
            team_players = self.players_df[self.players_df['team'] == team_id]['id'].tolist()
            self.problem += (
                pulp.lpSum([self.player_vars[pid] for pid in team_players]) <= MAX_PLAYERS_PER_TEAM,
                f"Max_Players_Team_{team_id}"
            )
        
        logger.info(f"Model built: {'Robust' if self.robust else 'Deterministic'}")
    
    def solve(self) -> Dict:
        """
        Solve the optimization problem
        
        Returns:
            Dictionary with solution details
        """
        if self.problem is None:
            self.build_model()
        
        # Solve
        status = self.problem.solve(pulp.PULP_CBC_CMD(msg=0))
        
        if status != pulp.LpStatusOptimal:
            logger.error(f"Optimization failed with status: {pulp.LpStatus[status]}")
            return None
        
        # Extract solution
        selected_player_ids = [
            pid for pid in self.player_vars 
            if pulp.value(self.player_vars[pid]) == 1
        ]
        
        captain_id = [
            pid for pid in self.captain_vars 
            if pulp.value(self.captain_vars[pid]) == 1
        ][0]
        
        # Get player details
        selected_players = self.players_df[
            self.players_df['id'].isin(selected_player_ids)
        ].copy()
        
        selected_players['is_captain'] = selected_players['id'] == captain_id
        
        # Calculate total cost and expected points
        total_cost = selected_players['cost'].sum()
        expected_total = selected_players['expected_points'].sum()
        captain_bonus = selected_players[selected_players['is_captain']]['expected_points'].values[0]
        expected_total += captain_bonus  # Captain gets double points
        
        # Formation
        formation = self._get_formation(selected_players)
        
        self.solution = {
            'status': pulp.LpStatus[status],
            'selected_players': selected_players,
            'captain_id': captain_id,
            'total_cost': total_cost,
            'budget_remaining': self.budget - total_cost,
            'expected_points': expected_total,
            'formation': formation,
            'objective_value': pulp.value(self.problem.objective)
        }
        
        logger.info(f"Optimization successful: {formation} formation")
        logger.info(f"Expected points: {expected_total:.2f}")
        logger.info(f"Total cost: {total_cost:.1f}M (Budget remaining: {self.budget - total_cost:.1f}M)")
        
        return self.solution
    
    def _get_formation(self, players: pd.DataFrame) -> str:
        """
        Get formation string (e.g., '3-5-2')
        
        Args:
            players: DataFrame with selected players
            
        Returns:
            Formation string
        """
        gk = len(players[players['position'] == 'GKP'])
        def_count = len(players[players['position'] == 'DEF'])
        mid = len(players[players['position'] == 'MID'])
        fwd = len(players[players['position'] == 'FWD'])
        
        return f"{def_count}-{mid}-{fwd}"
    
    def add_must_include_constraint(self, player_ids: List[int]):
        """
        Add constraint to force inclusion of specific players
        
        Args:
            player_ids: List of player IDs that must be included
        """
        if self.problem is None:
            self.build_model()
        
        for pid in player_ids:
            if pid in self.player_vars:
                self.problem += (
                    self.player_vars[pid] == 1,
                    f"Must_Include_Player_{pid}"
                )
                logger.info(f"Added must-include constraint for player {pid}")
    
    def add_must_exclude_constraint(self, player_ids: List[int]):
        """
        Add constraint to force exclusion of specific players
        
        Args:
            player_ids: List of player IDs that must be excluded
        """
        if self.problem is None:
            self.build_model()
        
        for pid in player_ids:
            if pid in self.player_vars:
                self.problem += (
                    self.player_vars[pid] == 0,
                    f"Must_Exclude_Player_{pid}"
                )
                logger.info(f"Added must-exclude constraint for player {pid}")
    
    def print_solution(self):
        """Print the solution in a readable format"""
        if self.solution is None:
            print("No solution available. Run solve() first.")
            return
        
        print("\n" + "="*80)
        print(f"FPL OPTIMAL TEAM - {self.solution['formation']} Formation")
        print("="*80)
        
        players = self.solution['selected_players'].copy()
        
        # Sort by position order
        position_order = {'GKP': 0, 'DEF': 1, 'MID': 2, 'FWD': 3}
        players['pos_order'] = players['position'].map(position_order)
        players = players.sort_values(['pos_order', 'expected_points'], ascending=[True, False])
        
        for _, player in players.iterrows():
            captain_mark = " (C)" if player['is_captain'] else ""
            print(f"{player['position']:4} | {player['web_name']:20} | "
                  f"{player['team_name']:15} | £{player['cost']:.1f}M | "
                  f"Exp: {player['expected_points']:.1f} pts{captain_mark}")
        
        print("-"*80)
        print(f"Total Cost: £{self.solution['total_cost']:.1f}M "
              f"(Remaining: £{self.solution['budget_remaining']:.1f}M)")
        print(f"Expected Points: {self.solution['expected_points']:.1f}")
        print("="*80 + "\n")


if __name__ == "__main__":
    # Test with dummy data
    import numpy as np
    
    # Create sample players
    np.random.seed(42)
    n_players = 100
    
    players = {
        'id': range(1, n_players + 1),
        'web_name': [f'Player{i}' for i in range(1, n_players + 1)],
        'position': np.random.choice(['GKP', 'DEF', 'MID', 'FWD'], n_players, 
                                    p=[0.1, 0.3, 0.4, 0.2]),
        'team': np.random.randint(1, 21, n_players),
        'team_name': [f'Team{i%20}' for i in range(n_players)],
        'cost': np.random.uniform(4.0, 13.0, n_players),
        'total_points': np.random.randint(0, 200, n_players)
    }
    
    players_df = pd.DataFrame(players)
    expected_points = {pid: np.random.uniform(2, 10) for pid in players_df['id']}
    
    # Test deterministic optimization
    print("Testing Deterministic Optimization:")
    optimizer = FPLOptimizer(players_df, expected_points)
    solution = optimizer.solve()
    optimizer.print_solution()
    
    # Test robust optimization
    print("\nTesting Robust Optimization:")
    robust_optimizer = FPLOptimizer(players_df, expected_points, robust=True)
    robust_solution = robust_optimizer.solve()
    robust_optimizer.print_solution()
