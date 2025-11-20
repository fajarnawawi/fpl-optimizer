"""
Utility functions for FPL Optimizer
"""

import json
import pandas as pd
from typing import Dict, List, Optional
from datetime import datetime
import logging

from config import SQUAD_FILE, RESULTS_FILE

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_current_squad() -> Dict:
    """
    Load current squad from file
    
    Returns:
        Dict with squad information
    """
    try:
        with open(SQUAD_FILE, 'r') as f:
            squad_data = json.load(f)
        logger.info(f"Loaded current squad from {SQUAD_FILE}")
        return squad_data
    except FileNotFoundError:
        logger.warning(f"Squad file not found: {SQUAD_FILE}")
        return {
            'squad': [],
            'budget': 0.0,
            'free_transfers': 1
        }


def save_current_squad(squad_data: Dict):
    """
    Save current squad to file
    
    Args:
        squad_data: Dictionary with squad information
    """
    with open(SQUAD_FILE, 'w') as f:
        json.dump(squad_data, f, indent=2)
    logger.info(f"Saved current squad to {SQUAD_FILE}")


def create_squad_template():
    """Create a template squad file with instructions"""
    template = {
        "_comment": "FPL Squad Template - Replace with your actual squad",
        "_instructions": [
            "Get player IDs from FPL API: https://fantasy.premierleague.com/api/bootstrap-static/",
            "Or use the player's web_name and the optimizer will match it",
            "budget: Your available budget for transfers (in millions)",
            "free_transfers: Number of free transfers available"
        ],
        "squad": [
            {
                "id": 0,
                "name": "Player Name",
                "position": "GKP",
                "team": "Team Name",
                "cost": 4.5
            },
            "... add 14 more players for a total of 15"
        ],
        "budget": 0.5,
        "free_transfers": 1
    }
    
    with open(SQUAD_FILE, 'w') as f:
        json.dump(template, f, indent=2)
    
    print(f"Created squad template at {SQUAD_FILE}")
    print("Please fill in your current squad details.")


def save_gameweek_result(gameweek: int, method: str, 
                         starting_11: pd.DataFrame, captain_id: int,
                         expected_points: float, actual_points: Optional[float] = None):
    """
    Save gameweek optimization result
    
    Args:
        gameweek: Gameweek number
        method: Prediction method used
        starting_11: DataFrame with selected players
        captain_id: ID of captain
        expected_points: Expected points from optimization
        actual_points: Actual points achieved (if known)
    """
    try:
        with open(RESULTS_FILE, 'r') as f:
            results = json.load(f)
    except FileNotFoundError:
        results = {'gameweeks': []}
    
    result_entry = {
        'gameweek': gameweek,
        'timestamp': datetime.now().isoformat(),
        'method': method,
        'formation': get_formation_string(starting_11),
        'starting_11': starting_11[['id', 'web_name', 'position', 'team_name', 'cost']].to_dict('records'),
        'captain_id': captain_id,
        'captain_name': starting_11[starting_11['id'] == captain_id]['web_name'].values[0],
        'expected_points': expected_points,
        'actual_points': actual_points,
        'total_cost': starting_11['cost'].sum()
    }
    
    # Update or append
    existing = [r for r in results['gameweeks'] if r['gameweek'] == gameweek and r['method'] == method]
    if existing:
        # Update existing entry
        for i, r in enumerate(results['gameweeks']):
            if r['gameweek'] == gameweek and r['method'] == method:
                results['gameweeks'][i] = result_entry
                break
    else:
        results['gameweeks'].append(result_entry)
    
    # Sort by gameweek
    results['gameweeks'] = sorted(results['gameweeks'], key=lambda x: x['gameweek'])
    
    with open(RESULTS_FILE, 'w') as f:
        json.dump(results, f, indent=2)
    
    logger.info(f"Saved GW{gameweek} result for method '{method}'")


def get_formation_string(players: pd.DataFrame) -> str:
    """
    Get formation string from players DataFrame
    
    Args:
        players: DataFrame with selected players
        
    Returns:
        Formation string (e.g., '3-5-2')
    """
    def_count = len(players[players['position'] == 'DEF'])
    mid_count = len(players[players['position'] == 'MID'])
    fwd_count = len(players[players['position'] == 'FWD'])
    
    return f"{def_count}-{mid_count}-{fwd_count}"


def print_comparison_table(results: Dict[str, Dict]):
    """
    Print comparison table of different methods
    
    Args:
        results: Dict mapping method name to results dict
    """
    print("\n" + "="*100)
    print("METHOD COMPARISON")
    print("="*100)
    print(f"{'Method':<25} | {'Formation':<10} | {'Expected Pts':<12} | {'Cost':<10} | {'Captain':<20}")
    print("-"*100)
    
    for method, result in sorted(results.items(), key=lambda x: x[1]['expected_points'], reverse=True):
        print(f"{method:<25} | {result['formation']:<10} | "
              f"{result['expected_points']:>12.2f} | "
              f"£{result['total_cost']:>7.1f}M | "
              f"{result['captain_name']:<20}")
    
    print("="*100 + "\n")


def match_player_by_name(name: str, players_df: pd.DataFrame) -> Optional[int]:
    """
    Match a player name to a player ID
    
    Args:
        name: Player name (web_name or full name)
        players_df: DataFrame with all players
        
    Returns:
        Player ID or None if not found
    """
    # Try exact match on web_name
    exact_match = players_df[players_df['web_name'].str.lower() == name.lower()]
    if not exact_match.empty:
        return exact_match.iloc[0]['id']
    
    # Try partial match
    partial_match = players_df[players_df['web_name'].str.lower().str.contains(name.lower())]
    if not partial_match.empty:
        if len(partial_match) == 1:
            return partial_match.iloc[0]['id']
        else:
            logger.warning(f"Multiple matches found for '{name}': {partial_match['web_name'].tolist()}")
            return partial_match.iloc[0]['id']
    
    # Try full name match
    players_df['full_name'] = players_df['first_name'] + ' ' + players_df['second_name']
    full_match = players_df[players_df['full_name'].str.lower().str.contains(name.lower())]
    if not full_match.empty:
        return full_match.iloc[0]['id']
    
    logger.warning(f"No match found for player name: '{name}'")
    return None


def get_squad_player_ids(squad_data: Dict, players_df: pd.DataFrame) -> List[int]:
    """
    Get player IDs from squad data, matching by name if necessary
    
    Args:
        squad_data: Squad dictionary
        players_df: DataFrame with all players
        
    Returns:
        List of player IDs
    """
    player_ids = []
    
    for player in squad_data.get('squad', []):
        if 'id' in player and player['id'] > 0:
            player_ids.append(player['id'])
        elif 'name' in player:
            pid = match_player_by_name(player['name'], players_df)
            if pid:
                player_ids.append(pid)
    
    return player_ids


def suggest_transfers(current_squad_ids: List[int], 
                     optimal_squad_ids: List[int],
                     players_df: pd.DataFrame,
                     max_transfers: int = 1) -> List[Dict]:
    """
    Suggest transfers to move from current squad to optimal squad
    
    Args:
        current_squad_ids: List of current player IDs
        optimal_squad_ids: List of optimal player IDs
        players_df: DataFrame with all players
        max_transfers: Maximum number of transfers to suggest
        
    Returns:
        List of transfer suggestions
    """
    current_set = set(current_squad_ids)
    optimal_set = set(optimal_squad_ids)
    
    # Players to transfer out
    to_remove = current_set - optimal_set
    # Players to transfer in
    to_add = optimal_set - current_set
    
    transfers = []
    
    for _ in range(min(max_transfers, len(to_remove), len(to_add))):
        # Find best transfer (highest expected points gain)
        best_transfer = None
        best_gain = -float('inf')
        
        for out_id in to_remove:
            for in_id in to_add:
                out_player = players_df[players_df['id'] == out_id].iloc[0]
                in_player = players_df[players_df['id'] == in_id].iloc[0]
                
                # Check if transfer is valid (position and budget)
                if out_player['position'] == in_player['position']:
                    points_gain = in_player['expected_points'] - out_player['expected_points']
                    cost_diff = in_player['cost'] - out_player['cost']
                    
                    if points_gain > best_gain:
                        best_gain = points_gain
                        best_transfer = {
                            'out_id': out_id,
                            'out_name': out_player['web_name'],
                            'out_cost': out_player['cost'],
                            'in_id': in_id,
                            'in_name': in_player['web_name'],
                            'in_cost': in_player['cost'],
                            'cost_diff': cost_diff,
                            'points_gain': points_gain
                        }
        
        if best_transfer:
            transfers.append(best_transfer)
            to_remove.remove(best_transfer['out_id'])
            to_add.remove(best_transfer['in_id'])
        else:
            break
    
    return transfers


def print_transfers(transfers: List[Dict]):
    """Print transfer suggestions in a readable format"""
    if not transfers:
        print("\nNo transfers needed - your squad is optimal!")
        return
    
    print("\n" + "="*80)
    print("RECOMMENDED TRANSFERS")
    print("="*80)
    
    for i, transfer in enumerate(transfers, 1):
        print(f"\nTransfer {i}:")
        print(f"  OUT: {transfer['out_name']} (£{transfer['out_cost']:.1f}M)")
        print(f"  IN:  {transfer['in_name']} (£{transfer['in_cost']:.1f}M)")
        print(f"  Cost diff: £{transfer['cost_diff']:.1f}M")
        print(f"  Expected points gain: {transfer['points_gain']:.1f}")
    
    total_cost = sum(t['cost_diff'] for t in transfers)
    total_gain = sum(t['points_gain'] for t in transfers)
    
    print("-"*80)
    print(f"Total cost: £{total_cost:.1f}M")
    print(f"Total expected gain: {total_gain:.1f} points")
    print("="*80 + "\n")


if __name__ == "__main__":
    # Test utility functions
    print("Testing utility functions...")
    
    # Create template
    create_squad_template()
    print("✓ Squad template created")
