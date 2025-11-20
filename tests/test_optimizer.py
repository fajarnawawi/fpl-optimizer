"""
Test suite for FPL Optimizer
Run with: pytest tests/test_optimizer.py
"""

import pytest
import pandas as pd
import numpy as np
from src.optimizer import FPLOptimizer
from src.models import PredictionModels, estimate_expected_points
from src.fpl_api import FPLAPIClient


class TestPredictionModels:
    """Test prediction model calculations"""
    
    def test_simple_average(self):
        points = [2, 4, 6, 8, 10]
        result = PredictionModels.simple_average(points)
        assert result == 6.0
    
    def test_weighted_average(self):
        points = [2, 4, 6, 8, 10]
        result = PredictionModels.weighted_average(points)
        # More recent points should have higher weight
        assert result > 6.0  # Should be > simple average
        assert result <= 10.0
    
    def test_monte_carlo(self):
        points = [5, 5, 5, 5, 5]
        result = PredictionModels.monte_carlo_simulation(points, n_simulations=100)
        # Should be close to 5 with constant values
        assert 4.5 <= result <= 5.5
    
    def test_empty_history(self):
        """Test handling of empty history"""
        result = PredictionModels.simple_average([])
        assert result == 0.0
        
        result = PredictionModels.weighted_average([])
        assert result == 0.0


class TestOptimizer:
    """Test integer programming optimizer"""
    
    @pytest.fixture
    def sample_players(self):
        """Create sample player data"""
        np.random.seed(42)
        
        players = {
            'id': list(range(1, 101)),
            'web_name': [f'Player{i}' for i in range(1, 101)],
            'position': ['GKP'] * 10 + ['DEF'] * 30 + ['MID'] * 40 + ['FWD'] * 20,
            'team': np.random.randint(1, 21, 100),
            'team_name': [f'Team{i%20}' for i in range(100)],
            'cost': np.random.uniform(4.0, 13.0, 100),
            'total_points': np.random.randint(0, 200, 100)
        }
        
        return pd.DataFrame(players)
    
    @pytest.fixture
    def expected_points(self, sample_players):
        """Create expected points for sample players"""
        return {pid: np.random.uniform(2, 10) for pid in sample_players['id']}
    
    def test_optimizer_initialization(self, sample_players, expected_points):
        """Test optimizer can be initialized"""
        optimizer = FPLOptimizer(sample_players, expected_points)
        assert optimizer is not None
        assert optimizer.budget == 83.5
    
    def test_optimizer_builds_model(self, sample_players, expected_points):
        """Test that model building succeeds"""
        optimizer = FPLOptimizer(sample_players, expected_points)
        optimizer.build_model()
        assert optimizer.problem is not None
        assert len(optimizer.player_vars) > 0
    
    def test_optimizer_finds_solution(self, sample_players, expected_points):
        """Test that optimizer finds a valid solution"""
        optimizer = FPLOptimizer(sample_players, expected_points)
        solution = optimizer.solve()
        
        assert solution is not None
        assert solution['status'] == 'Optimal'
        
        # Check constraints
        selected = solution['selected_players']
        assert len(selected) == 11  # Exactly 11 players
        assert solution['total_cost'] <= 83.5  # Within budget
        
        # Check formation
        gk = len(selected[selected['position'] == 'GKP'])
        def_count = len(selected[selected['position'] == 'DEF'])
        mid = len(selected[selected['position'] == 'MID'])
        fwd = len(selected[selected['position'] == 'FWD'])
        
        assert gk == 1
        assert 3 <= def_count <= 5
        assert 3 <= mid <= 5
        assert 1 <= fwd <= 3
        
        # Check team constraint
        team_counts = selected['team'].value_counts()
        assert all(team_counts <= 3)
        
        # Check captain
        captains = selected[selected['is_captain']]
        assert len(captains) == 1
    
    def test_robust_optimization(self, sample_players, expected_points):
        """Test robust optimization variant"""
        optimizer = FPLOptimizer(
            sample_players, 
            expected_points,
            robust=True,
            uncertainty_margin=0.2
        )
        solution = optimizer.solve()
        
        assert solution is not None
        # Robust solution should still be valid
        assert len(solution['selected_players']) == 11
    
    def test_must_include_constraint(self, sample_players, expected_points):
        """Test adding must-include constraint"""
        optimizer = FPLOptimizer(sample_players, expected_points)
        
        # Force include first midfielder
        mid_players = sample_players[sample_players['position'] == 'MID']
        forced_player_id = mid_players.iloc[0]['id']
        
        optimizer.add_must_include_constraint([forced_player_id])
        solution = optimizer.solve()
        
        assert forced_player_id in solution['selected_players']['id'].values


class TestFPLAPI:
    """Test FPL API client"""
    
    def test_api_client_initialization(self):
        """Test API client can be initialized"""
        client = FPLAPIClient()
        assert client is not None
    
    @pytest.mark.integration
    def test_get_bootstrap_data(self):
        """Integration test - fetches real data from FPL API"""
        client = FPLAPIClient()
        data = client.get_bootstrap_data()
        
        assert data is not None
        assert 'elements' in data
        assert 'teams' in data
        assert 'events' in data
    
    @pytest.mark.integration
    def test_get_all_players(self):
        """Integration test - fetches player data"""
        client = FPLAPIClient()
        players = client.get_all_players()
        
        assert len(players) > 0
        assert 'id' in players.columns
        assert 'web_name' in players.columns
        assert 'position' in players.columns
        assert 'cost' in players.columns


class TestEndToEnd:
    """End-to-end integration tests"""
    
    @pytest.mark.integration
    def test_full_optimization_pipeline(self):
        """Test complete optimization pipeline with real data"""
        # This test requires internet connection
        client = FPLAPIClient()
        
        # Get player data
        players_df = client.get_all_players()
        assert len(players_df) > 0
        
        # Simple expected points (just use total points as proxy)
        expected_points = dict(zip(players_df['id'], players_df['total_points']))
        
        # Run optimization
        optimizer = FPLOptimizer(players_df, expected_points)
        solution = optimizer.solve()
        
        assert solution is not None
        assert len(solution['selected_players']) == 11


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, '-v'])
