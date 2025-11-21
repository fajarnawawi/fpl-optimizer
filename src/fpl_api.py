"""
FPL API Client - Fetches data from Fantasy Premier League API
"""

import requests
import pandas as pd
import json
import logging
from typing import Dict, List, Optional
from datetime import datetime

from config import (
    FPL_API_BASE_URL,
    POSITION_MAP,
    HISTORY_FILE
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FPLAPIClient:
    """Client for interacting with FPL API"""
    
    def __init__(self):
        self.base_url = FPL_API_BASE_URL
        self.session = requests.Session()
        self._bootstrap_data = None
        self._current_gameweek = None
        
    def get_bootstrap_data(self, force_refresh: bool = False) -> Dict:
        """
        Fetch bootstrap-static data which contains all players, teams, gameweeks
        
        Args:
            force_refresh: Force refresh even if data is cached
            
        Returns:
            Dictionary containing bootstrap data
        """
        if self._bootstrap_data is not None and not force_refresh:
            return self._bootstrap_data
            
        try:
            url = f"{self.base_url}bootstrap-static/"
            response = self.session.get(url)
            response.raise_for_status()
            self._bootstrap_data = response.json()
            logger.info("Successfully fetched bootstrap data")
            return self._bootstrap_data
        except requests.RequestException as e:
            logger.error(f"Error fetching bootstrap data: {e}")
            raise
    
    def get_current_gameweek(self) -> int:
        """Get the current gameweek number"""
        if self._current_gameweek is not None:
            return self._current_gameweek
            
        data = self.get_bootstrap_data()
        for event in data['events']:
            if event['is_current']:
                self._current_gameweek = event['id']
                return self._current_gameweek
        
        # If no current gameweek, return next gameweek
        for event in data['events']:
            if event['is_next']:
                self._current_gameweek = event['id']
                return self._current_gameweek
        
        return 1  # Default to GW1
    
    def get_all_players(self) -> pd.DataFrame:
        """
        Get all players with their current data
        
        Returns:
            DataFrame with player information
        """
        data = self.get_bootstrap_data()
        players_df = pd.DataFrame(data['elements'])
        
        # Add position and team names
        teams = {team['id']: team['name'] for team in data['teams']}
        players_df['team_name'] = players_df['team'].map(teams)
        players_df['position'] = players_df['element_type'].map(POSITION_MAP)
        
        # Convert cost from API format (e.g., 105 = 10.5M)
        players_df['cost'] = players_df['now_cost'] / 10.0
        
        # Relevant columns
        columns = [
            'id', 'web_name', 'first_name', 'second_name',
            'team', 'team_name', 'position', 'element_type',
            'cost', 'selected_by_percent', 'form',
            'total_points', 'points_per_game', 'minutes',
            'goals_scored', 'assists', 'clean_sheets',
            'goals_conceded', 'bonus', 'influence',
            'creativity', 'threat', 'ict_index',
            'expected_goals', 'expected_assists',
            'expected_goal_involvements', 'expected_goals_conceded',
            'starts', 'yellow_cards', 'red_cards',
            'chance_of_playing_next_round'
        ]
        
        # Only include columns that exist
        available_columns = [col for col in columns if col in players_df.columns]
        
        return players_df[available_columns]
    
    def get_player_history(self, player_id: int) -> pd.DataFrame:
        """
        Get gameweek history for a specific player
        
        Args:
            player_id: FPL player ID
            
        Returns:
            DataFrame with player's gameweek history
        """
        try:
            url = f"{self.base_url}element-summary/{player_id}/"
            response = self.session.get(url)
            response.raise_for_status()
            data = response.json()
            
            history_df = pd.DataFrame(data['history'])
            return history_df
        except requests.RequestException as e:
            logger.error(f"Error fetching player {player_id} history: {e}")
            return pd.DataFrame()
    
    def get_player_histories_bulk(self, player_ids: List[int], 
                                   current_gw: int) -> Dict[int, pd.DataFrame]:
        """
        Get histories for multiple players up to current gameweek
        
        Args:
            player_ids: List of player IDs
            current_gw: Current gameweek number
            
        Returns:
            Dictionary mapping player_id to their history DataFrame
        """
        histories = {}
        
        for player_id in player_ids:
            history = self.get_player_history(player_id)
            if not history.empty:
                # Filter to only include completed gameweeks
                history = history[history['round'] < current_gw]
                histories[player_id] = history
        
        logger.info(f"Fetched histories for {len(histories)} players")
        return histories
    
    def get_player_points_history(self, player_id: int, 
                                   num_weeks: Optional[int] = None) -> List[float]:
        """
        Get list of points scored by player in recent gameweeks
        
        Args:
            player_id: FPL player ID
            num_weeks: Number of recent weeks to fetch (None = all)
            
        Returns:
            List of points in chronological order
        """
        history = self.get_player_history(player_id)
        if history.empty:
            return []
        
        points = history['total_points'].tolist()
        
        if num_weeks is not None and num_weeks > 0:
            points = points[-num_weeks:]
        
        return points
    
    def save_player_data(self, players_df: pd.DataFrame, 
                        histories: Dict[int, pd.DataFrame]):
        """
        Save player data and histories to file
        
        Args:
            players_df: DataFrame with current player data
            histories: Dictionary of player histories
        """
        data_to_save = {
            'timestamp': datetime.now().isoformat(),
            'gameweek': self.get_current_gameweek(),
            'players': players_df.to_dict('records'),
            'histories': {
                str(pid): hist.to_dict('records') 
                for pid, hist in histories.items()
            }
        }
        
        with open(HISTORY_FILE, 'w') as f:
            json.dump(data_to_save, f, indent=2)
        
        logger.info(f"Saved player data to {HISTORY_FILE}")
    
    def load_player_data(self) -> tuple:
        """
        Load previously saved player data
        
        Returns:
            Tuple of (players_df, histories_dict)
        """
        try:
            with open(HISTORY_FILE, 'r') as f:
                data = json.load(f)
            
            players_df = pd.DataFrame(data['players'])
            histories = {
                int(pid): pd.DataFrame(hist) 
                for pid, hist in data['histories'].items()
            }
            
            logger.info(f"Loaded player data from {HISTORY_FILE}")
            return players_df, histories
        except FileNotFoundError:
            logger.warning(f"No saved data found at {HISTORY_FILE}")
            return None, None
    
    def get_fixtures(self, gameweek: Optional[int] = None) -> pd.DataFrame:
        """
        Get fixtures for a specific gameweek

        Args:
            gameweek: Gameweek number (None = next gameweek)

        Returns:
            DataFrame with fixture information
        """
        try:
            url = f"{self.base_url}fixtures/"
            if gameweek:
                url += f"?event={gameweek}"

            response = self.session.get(url)
            response.raise_for_status()
            fixtures = response.json()

            return pd.DataFrame(fixtures)
        except requests.RequestException as e:
            logger.error(f"Error fetching fixtures: {e}")
            return pd.DataFrame()

    def get_next_fixture_difficulty(self, current_gw: int) -> Dict[int, int]:
        """
        Get the difficulty rating of the next fixture for each team

        Args:
            current_gw: Current gameweek number

        Returns:
            Dict mapping team_id to difficulty rating (1-5)
        """
        next_gw = current_gw + 1
        fixtures_df = self.get_fixtures(next_gw)

        if fixtures_df.empty:
            # Return default difficulty of 3 if no fixtures found (e.g. end of season)
            return {i: 3 for i in range(1, 21)}

        team_difficulty = {}

        for _, row in fixtures_df.iterrows():
            # Map home team difficulty
            team_difficulty[row['team_h']] = row['team_h_difficulty']
            # Map away team difficulty
            team_difficulty[row['team_a']] = row['team_a_difficulty']

        # Fill missing teams (blanks) with high difficulty (prevent selection)
        for i in range(1, 21):
            if i not in team_difficulty:
                team_difficulty[i] = 5

        return team_difficulty


if __name__ == "__main__":
    # Test the API client
    client = FPLAPIClient()
    
    print(f"Current Gameweek: {client.get_current_gameweek()}")
    
    players = client.get_all_players()
    print(f"\nTotal Players: {len(players)}")
    print("\nTop 5 players by total points:")
    print(players.nlargest(5, 'total_points')[['web_name', 'position', 'team_name', 'cost', 'total_points']])
    
    # Test fetching player history
    top_player_id = players.nlargest(1, 'total_points').iloc[0]['id']
    history = client.get_player_history(top_player_id)
    print(f"\nHistory for player {top_player_id}:")
    print(history.head())
