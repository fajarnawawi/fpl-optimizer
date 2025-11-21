"""
Strategic Overlays for FPL Optimization
Implements Section 5.4: Risk Management and Differentials (EO)
"""

from typing import Dict
import pandas as pd

class StrategyOverlay:
    @staticmethod
    def apply_strategy(cpv_scores: Dict[int, float],
                      players_df: pd.DataFrame,
                      mode: str = 'standard') -> Dict[int, float]:
        """
        Adjust CPV scores based on strategy mode and Effective Ownership (EO)

        Args:
            cpv_scores: Base CPV scores
            players_df: DataFrame containing 'selected_by_percent'
            mode: 'standard', 'rank_protection', or 'rank_climbing'
        """
        adjusted_scores = {}

        for pid, score in cpv_scores.items():
            player = players_df[players_df['id'] == pid].iloc[0]

            # Use selected_by_percent as proxy for EO
            ownership = float(player['selected_by_percent']) / 100.0

            if mode == 'rank_protection':
                # Boost high ownership players to minimize variance
                # "Go with the crowd"
                multiplier = 1.0 + (ownership * 0.5)
                adjusted_scores[pid] = score * multiplier

            elif mode == 'rank_climbing':
                # Penalize high ownership, boost differentials
                # Prioritize CPV / EO ratio
                multiplier = 1.0 + (1.0 - ownership)
                adjusted_scores[pid] = score * multiplier

            else:
                # Standard: Maximize raw points
                adjusted_scores[pid] = score

        return adjusted_scores
