"""
Prediction Models for Expected Points
Implements methods from the paper:
- Weighted Average (best consistent performer)
- Monte Carlo Simulation (best consistent performer)  
- Simple Average
- Exponential Smoothing
- ARIMA
- Linear Regression
- Hybrid ML approach (highest peak score)
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Optional
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from statsmodels.tsa.arima.model import ARIMA
import logging

from config import (
    MONTE_CARLO_SIMULATIONS,
    HYBRID_ML_RATIO,
    RIDGE_ALPHA,
    SCORING_FEATURES
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PredictionModels:
    """Collection of prediction models for estimating expected points"""
    
    @staticmethod
    def simple_average(points_history: List[float]) -> float:
        """
        Simple average of all historical points
        
        Args:
            points_history: List of points in chronological order
            
        Returns:
            Average points
        """
        if not points_history:
            return 0.0
        return np.mean(points_history)
    
    @staticmethod
    def weighted_average(points_history: List[float]) -> float:
        """
        Weighted average giving more weight to recent performances
        As per paper: weight[i] = i / sum(1 to N)
        
        Args:
            points_history: List of points in chronological order
            
        Returns:
            Weighted average points
        """
        if not points_history:
            return 0.0
        
        n = len(points_history)
        weights = np.array([i for i in range(1, n + 1)])
        weights = weights / np.sum(weights)
        
        return np.sum(weights * np.array(points_history))
    
    @staticmethod
    def exponential_smoothing(points_history: List[float], 
                             weeks_ahead: int = 1) -> float:
        """
        Exponential smoothing with trend (Holt-Winters)
        
        Args:
            points_history: List of points in chronological order
            weeks_ahead: Number of weeks to forecast ahead
            
        Returns:
            Forecasted points (average of forecasts)
        """
        if len(points_history) < 4:
            return PredictionModels.weighted_average(points_history)
        
        try:
            model = ExponentialSmoothing(
                points_history, 
                trend='add',
                seasonal=None,
                initialization_method='estimated'
            )
            fitted_model = model.fit()
            forecast = fitted_model.forecast(weeks_ahead)
            return np.mean(forecast)
        except Exception as e:
            logger.warning(f"Exponential smoothing failed: {e}. Using weighted average.")
            return PredictionModels.weighted_average(points_history)
    
    @staticmethod
    def monte_carlo_simulation(points_history: List[float], 
                               n_simulations: int = MONTE_CARLO_SIMULATIONS) -> float:
        """
        Monte Carlo simulation - sample from historical distribution
        
        Args:
            points_history: List of points in chronological order
            n_simulations: Number of simulations to run
            
        Returns:
            Expected points from simulation
        """
        if not points_history:
            return 0.0
        
        # Sample with replacement from historical points
        simulated_points = np.random.choice(
            points_history, 
            size=n_simulations, 
            replace=True
        )
        
        return np.mean(simulated_points)
    
    @staticmethod
    def bootstrapping(points_history: List[float],
                     n_simulations: int = MONTE_CARLO_SIMULATIONS) -> float:
        """
        Non-parametric bootstrapping
        
        Args:
            points_history: List of points in chronological order
            n_simulations: Number of bootstrap samples
            
        Returns:
            Expected points from bootstrapping
        """
        return PredictionModels.monte_carlo_simulation(points_history, n_simulations)
    
    @staticmethod
    def arima_forecast(points_history: List[float],
                      order: tuple = (0, 1, 1),
                      weeks_ahead: int = 12) -> float:
        """
        ARIMA time series forecasting
        
        Args:
            points_history: List of points in chronological order
            order: ARIMA(p,d,q) order
            weeks_ahead: Number of weeks to forecast
            
        Returns:
            Mean of forecasted points
        """
        if len(points_history) < 10:
            return PredictionModels.weighted_average(points_history)
        
        try:
            model = ARIMA(points_history, order=order)
            fitted_model = model.fit()
            forecast = fitted_model.forecast(steps=weeks_ahead)
            return np.mean(forecast)
        except Exception as e:
            logger.warning(f"ARIMA forecast failed: {e}. Using weighted average.")
            return PredictionModels.weighted_average(points_history)
    
    @staticmethod
    def linear_regression_forecast(points_history: List[float],
                                   weeks_ahead: int = 12) -> float:
        """
        Simple linear regression on week number
        
        Args:
            points_history: List of points in chronological order
            weeks_ahead: Number of weeks to forecast
            
        Returns:
            Mean of forecasted points
        """
        if len(points_history) < 3:
            return PredictionModels.weighted_average(points_history)
        
        # Prepare data
        n = len(points_history)
        X = np.array(range(1, n + 1)).reshape(-1, 1)
        y = np.array(points_history)
        
        # Fit model
        from sklearn.linear_model import LinearRegression
        model = LinearRegression()
        model.fit(X, y)
        
        # Forecast
        future_weeks = np.array(range(n + 1, n + weeks_ahead + 1)).reshape(-1, 1)
        forecast = model.predict(future_weeks)
        
        # Clip negative predictions
        forecast = np.maximum(forecast, 0)
        
        return np.mean(forecast)


class HybridModel:
    """
    Hybrid ML model combining actual points with predictions from underlying features
    Uses Ridge regression with Shapley-informed features
    """
    
    def __init__(self, alpha: float = RIDGE_ALPHA):
        self.alpha = alpha
        self.models = {}  # One model per position
        self.scalers = {}
        self.feature_names = SCORING_FEATURES
        
    def prepare_features(self, player_data: pd.DataFrame, 
                        position: str) -> tuple:
        """
        Prepare features and target for a specific position
        
        Args:
            player_data: DataFrame with player statistics
            position: Position (GKP, DEF, MID, FWD)
            
        Returns:
            Tuple of (X, y) where X is features and y is total_points
        """
        # Filter by position
        pos_data = player_data[player_data['position'] == position].copy()
        
        if pos_data.empty:
            return None, None
        
        # Select features that exist in the data
        available_features = [f for f in self.feature_names if f in pos_data.columns]
        
        if not available_features:
            logger.warning(f"No features available for {position}")
            return None, None
        
        X = pos_data[available_features].fillna(0).values
        y = pos_data['total_points'].fillna(0).values
        
        return X, y
    
    def fit(self, player_data: pd.DataFrame):
        """
        Fit Ridge regression models for each position
        
        Args:
            player_data: DataFrame with all players and their stats
        """
        for position in ['GKP', 'DEF', 'MID', 'FWD']:
            X, y = self.prepare_features(player_data, position)
            
            if X is None or len(X) < 10:
                logger.warning(f"Insufficient data for {position}")
                continue
            
            # Normalize features
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)
            
            # Fit Ridge regression
            model = Ridge(alpha=self.alpha)
            model.fit(X_scaled, y)
            
            self.models[position] = model
            self.scalers[position] = scaler
            
            logger.info(f"Fitted hybrid model for {position}")
    
    def predict(self, player_data: pd.DataFrame) -> pd.Series:
        """
        Predict points for all players
        
        Args:
            player_data: DataFrame with player statistics
            
        Returns:
            Series with predicted points for each player
        """
        predictions = []
        
        for _, player in player_data.iterrows():
            position = player['position']
            
            if position not in self.models:
                predictions.append(0.0)
                continue
            
            # Prepare features
            available_features = [f for f in self.feature_names 
                                if f in player_data.columns]
            features = [player.get(f, 0) for f in available_features]
            X = np.array(features).reshape(1, -1)
            
            # Scale and predict
            X_scaled = self.scalers[position].transform(X)
            pred = self.models[position].predict(X_scaled)[0]
            predictions.append(max(0, pred))  # No negative predictions
        
        return pd.Series(predictions, index=player_data.index)
    
    def hybrid_score(self, player_data: pd.DataFrame, 
                    actual_points: pd.Series) -> pd.Series:
        """
        Create hybrid score combining actual and predicted points
        As per paper: 2:1 ratio (actual:predicted)
        
        Args:
            player_data: DataFrame with player statistics
            actual_points: Series with actual total points
            
        Returns:
            Series with hybrid scores
        """
        # Get predictions
        predicted_points = self.predict(player_data)
        
        # Normalize both to 0-1 range
        actual_norm = (actual_points - actual_points.min()) / (actual_points.max() - actual_points.min() + 1e-10)
        pred_norm = (predicted_points - predicted_points.min()) / (predicted_points.max() - predicted_points.min() + 1e-10)
        
        # Combine with 2:1 ratio
        a, b = HYBRID_ML_RATIO
        hybrid = (a * actual_norm + b * pred_norm) / (a + b)
        
        # Scale back to points range
        hybrid_scaled = hybrid * (actual_points.max() - actual_points.min()) + actual_points.min()
        
        return hybrid_scaled


def estimate_expected_points(player_histories: Dict[int, pd.DataFrame],
                            method: str = 'weighted_average',
                            weeks_to_end: int = 12) -> Dict[int, float]:
    """
    Estimate expected points for all players using specified method
    
    Args:
        player_histories: Dict mapping player_id to their history DataFrame
        method: Prediction method to use
        weeks_to_end: Weeks remaining in season (for forecasting methods)
        
    Returns:
        Dict mapping player_id to expected points
    """
    expected_points = {}
    
    for player_id, history in player_histories.items():
        if history.empty:
            expected_points[player_id] = 0.0
            continue
        
        points_list = history['total_points'].tolist()
        
        if method == 'simple_average':
            exp_pts = PredictionModels.simple_average(points_list)
        elif method == 'weighted_average':
            exp_pts = PredictionModels.weighted_average(points_list)
        elif method == 'exponential_smoothing':
            exp_pts = PredictionModels.exponential_smoothing(points_list, weeks_to_end)
        elif method == 'monte_carlo':
            exp_pts = PredictionModels.monte_carlo_simulation(points_list)
        elif method == 'bootstrapping':
            exp_pts = PredictionModels.bootstrapping(points_list)
        elif method == 'arima':
            exp_pts = PredictionModels.arima_forecast(points_list, weeks_ahead=weeks_to_end)
        elif method == 'linear_regression':
            exp_pts = PredictionModels.linear_regression_forecast(points_list, weeks_to_end)
        else:
            logger.warning(f"Unknown method {method}, using weighted_average")
            exp_pts = PredictionModels.weighted_average(points_list)
        
        expected_points[player_id] = max(0, exp_pts)  # No negative expectations
    
    return expected_points


if __name__ == "__main__":
    # Test prediction models
    sample_points = [2, 5, 8, 6, 3, 7, 9, 4, 6, 8, 7]
    
    print("Testing Prediction Models")
    print("=" * 50)
    print(f"Sample points: {sample_points}")
    print(f"\nSimple Average: {PredictionModels.simple_average(sample_points):.2f}")
    print(f"Weighted Average: {PredictionModels.weighted_average(sample_points):.2f}")
    print(f"Monte Carlo: {PredictionModels.monte_carlo_simulation(sample_points):.2f}")
    print(f"Exponential Smoothing: {PredictionModels.exponential_smoothing(sample_points):.2f}")
    print(f"ARIMA: {PredictionModels.arima_forecast(sample_points):.2f}")
    print(f"Linear Regression: {PredictionModels.linear_regression_forecast(sample_points):.2f}")
