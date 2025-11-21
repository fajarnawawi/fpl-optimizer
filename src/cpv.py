"""
Composite Player Viability (CPV) Calculator
Implements the Unified Framework from Section 4 of the Methodology
"""

import pandas as pd
import numpy as np
from typing import Dict, List
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CPVCalculator:
    def __init__(self, players_df: pd.DataFrame,
                 expected_points: Dict[int, float],
                 team_difficulty: Dict[int, int]):
        self.players = players_df.copy()
        self.xP = expected_points
        self.difficulty = team_difficulty

        # Weights from Methodology Table 4
        self.W_XP = 0.40   # Predicted Points
        self.W_FFI = 0.25  # Fixture & Form Index
        self.W_VCS = 0.15  # Value & Ceiling Score
        self.W_SSS = 0.20  # Sentiment & Status Signal

    def calculate_ffi(self, player: pd.Series) -> float:
        """
        Calculate Fixture & Form Index (FFI) with position-dependent weighting
        Section 2.3: Defenders (Fixtures > Form), Attackers (Form > Fixtures)
        """
        # Normalize Form (0-10 scale typically)
        form_score = float(player['form']) / 10.0
        form_score = max(0.0, min(1.0, form_score))

        # Normalize Fixture (FDR is 1-5, we want 1 to be high score)
        # Difficulty 1 -> 1.0, Difficulty 5 -> 0.0
        team_id = player['team']
        fdr = self.difficulty.get(team_id, 3)
        fixture_score = (5 - fdr) / 4.0

        # Position-dependent weighting
        pos = player['position']
        if pos in ['GKP', 'DEF']:
            # Defenders: 70% Fixture, 30% Form
            return (0.7 * fixture_score) + (0.3 * form_score)
        else:
            # Att/Mid: 30% Fixture, 70% Form
            return (0.3 * fixture_score) + (0.7 * form_score)

    def calculate_vcs(self, player: pd.Series) -> float:
        """
        Calculate Value & Ceiling Score (VCS)
        Combines Points Per Million (Value) with high-score potential (Ceiling)
        """
        # Value: Points per million
        if player['cost'] > 0:
            ppm = player['total_points'] / player['cost']
            # Normalize PPM (approx max 25)
            value_score = min(1.0, ppm / 25.0)
        else:
            value_score = 0

        # Ceiling: Use ICT index as proxy for explosive potential
        ict = float(player['ict_index'])
        # Normalize ICT (approx max 300)
        ceiling_score = min(1.0, ict / 300.0)

        return (0.5 * value_score) + (0.5 * ceiling_score)

    def calculate_sss(self, player: pd.Series) -> float:
        """
        Calculate Sentiment & Status Signal (SSS)
        Acts as a non-linear 'veto' mechanism for injuries (Section 4.2)
        """
        chance = player.get('chance_of_playing_next_round')

        # If chance is None, FPL considers it 100%
        if pd.isna(chance):
            return 1.0

        # Veto mechanism: If < 75% chance, effectively nullify the player
        if chance < 75:
            return 0.0
        else:
            return float(chance) / 100.0

    def calculate_all(self) -> Dict[int, float]:
        """Calculate final CPV scores for all players"""
        cpv_scores = {}

        # Normalize xP first (find max)
        max_xp = max(self.xP.values()) if self.xP else 1

        for _, player in self.players.iterrows():
            pid = player['id']

            # 1. Normalized Predicted Points
            raw_xp = self.xP.get(pid, 0)
            xp_score = raw_xp / max_xp

            # 2. Fixture & Form
            ffi_score = self.calculate_ffi(player)

            # 3. Value & Ceiling
            vcs_score = self.calculate_vcs(player)

            # 4. Status Signal (Veto)
            sss_multiplier = self.calculate_sss(player)

            # Composite Calculation
            # Note: SSS is used as a multiplier (veto), not just an additive component
            # per Section 4.2 logic "SSS... as a non-linear veto mechanism"

            weighted_sum = (
                (self.W_XP * xp_score * 100) +
                (self.W_FFI * ffi_score * 100) +
                (self.W_VCS * vcs_score * 100)
            )

            final_cpv = weighted_sum * sss_multiplier

            cpv_scores[pid] = final_cpv

        return cpv_scores
