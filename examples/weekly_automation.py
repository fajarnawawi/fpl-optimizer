"""
Example: Automated Weekly Optimization
Script that can be scheduled to run before each gameweek deadline
"""

import sys
sys.path.insert(0, '../src')

from fpl_api import FPLAPIClient
from models import estimate_expected_points
from optimizer import FPLOptimizer
from utils import (
    load_current_squad,
    save_gameweek_result,
    get_squad_player_ids,
    suggest_transfers,
    print_transfers
)
from datetime import datetime
import json


def weekly_optimization(method='weighted_average'):
    """
    Run weekly optimization and save results
    
    Args:
        method: Prediction method to use
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    print("="*80)
    print(f"FPL Weekly Optimization - {timestamp}")
    print(f"Method: {method}")
    print("="*80)
    
    # Initialize API client
    client = FPLAPIClient()
    current_gw = client.get_current_gameweek()
    
    print(f"\nCurrent Gameweek: {current_gw}")
    
    # Load current squad
    print("\nLoading your current squad...")
    squad_data = load_current_squad()
    
    # Fetch all players
    print("Fetching player data...")
    players_df = client.get_all_players()
    
    # Get your squad player IDs
    my_squad_ids = get_squad_player_ids(squad_data, players_df)
    
    if not my_squad_ids or len(my_squad_ids) < 11:
        print(f"\n⚠️  Warning: Only {len(my_squad_ids)} players found in your squad.")
        print("Please update data/my_squad.json with your current squad.")
        return
    
    print(f"✓ Found {len(my_squad_ids)} players in your squad")
    
    # Filter to your squad
    my_players = players_df[players_df['id'].isin(my_squad_ids)]
    
    # Get histories
    print("\nFetching player histories...")
    histories = client.get_player_histories_bulk(my_squad_ids, current_gw)
    print(f"✓ Got history for {len(histories)} players")
    
    # Calculate expected points
    print(f"\nCalculating expected points using {method}...")
    expected_points = estimate_expected_points(
        histories,
        method=method,
        weeks_to_end=38-current_gw
    )
    
    # Optimize starting 11 from your squad
    print("\nOptimizing starting 11...")
    optimizer = FPLOptimizer(
        players_df=my_players,
        expected_points=expected_points,
        budget=83.5
    )
    
    solution = optimizer.solve()
    
    if not solution:
        print("\n❌ Optimization failed!")
        return
    
    print("\n✓ Optimization successful!")
    
    # Display solution
    optimizer.print_solution()
    
    # Save results
    print("\nSaving results...")
    save_gameweek_result(
        gameweek=current_gw,
        method=method,
        starting_11=solution['selected_players'],
        captain_id=solution['captain_id'],
        expected_points=solution['expected_points']
    )
    
    # Also suggest transfers if optimizing from all players
    print("\n" + "="*80)
    print("TRANSFER SUGGESTIONS")
    print("="*80)
    
    print("\nOptimizing from ALL available players...")
    all_players = players_df.copy()
    all_histories = client.get_player_histories_bulk(
        all_players['id'].tolist()[:200],  # Limit for performance
        current_gw
    )
    
    all_expected = estimate_expected_points(
        all_histories,
        method=method,
        weeks_to_end=38-current_gw
    )
    
    # Filter to players with expected points
    all_players = all_players[all_players['id'].isin(all_expected.keys())]
    
    optimal_optimizer = FPLOptimizer(
        players_df=all_players,
        expected_points=all_expected,
        budget=83.5
    )
    
    optimal_solution = optimal_optimizer.solve()
    
    if optimal_solution:
        optimal_squad = optimal_solution['selected_players']['id'].tolist()
        
        # Suggest transfers
        max_transfers = squad_data.get('free_transfers', 1)
        transfers = suggest_transfers(
            my_squad_ids,
            optimal_squad,
            players_df,
            max_transfers=max_transfers
        )
        
        print_transfers(transfers)
        
        # Save transfer suggestions
        transfer_file = f'data/transfers_gw{current_gw}.json'
        with open(transfer_file, 'w') as f:
            json.dump({
                'gameweek': current_gw,
                'timestamp': timestamp,
                'method': method,
                'transfers': transfers,
                'optimal_squad': optimal_solution['selected_players'][
                    ['id', 'web_name', 'position', 'team_name', 'cost']
                ].to_dict('records')
            }, f, indent=2)
        
        print(f"\n✓ Transfer suggestions saved to {transfer_file}")
    
    # Summary
    print("\n" + "="*80)
    print("WEEKLY OPTIMIZATION SUMMARY")
    print("="*80)
    print(f"  Gameweek: {current_gw}")
    print(f"  Method: {method}")
    print(f"  Your Squad's Best 11: {solution['formation']}")
    print(f"  Expected Points: {solution['expected_points']:.2f}")
    print(f"  Captain: {solution['selected_players'][solution['selected_players']['is_captain']]['web_name'].values[0]}")
    if transfers:
        print(f"  Recommended Transfers: {len(transfers)}")
        for t in transfers:
            print(f"    • {t['out_name']} → {t['in_name']} (+{t['points_gain']:.1f} pts)")
    print("="*80)
    
    print("\n✅ Weekly optimization complete!")
    print(f"Results saved to data/gameweek_results.json")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Weekly FPL optimization')
    parser.add_argument(
        '--method',
        type=str,
        default='weighted_average',
        choices=['simple_average', 'weighted_average', 'exponential_smoothing',
                'monte_carlo', 'arima', 'linear_regression', 'hybrid'],
        help='Prediction method (default: weighted_average)'
    )
    
    args = parser.parse_args()
    
    try:
        weekly_optimization(method=args.method)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
