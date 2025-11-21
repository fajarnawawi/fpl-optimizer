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
            # Find player in dataframe
            player_rows = players_df[players_df['id'] == pid]
            if player_rows.empty:
                # Player not found, use unadjusted score
                adjusted_scores[pid] = score
                continue

            player = player_rows.iloc[0]

            # Use selected_by_percent as proxy for EO (with safe conversion)
            try:
                ownership_value = player.get('selected_by_percent', 0)
                if pd.isna(ownership_value) or ownership_value == '':
                    ownership_value = 0
                ownership = float(ownership_value) / 100.0
            except (ValueError, TypeError):
                ownership = 0.0

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
