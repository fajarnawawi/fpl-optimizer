"""
Example: Basic FPL Optimization
Demonstrates simple usage of the optimizer
"""

import sys
sys.path.insert(0, '../src')

from fpl_api import FPLAPIClient
from models import estimate_expected_points
from optimizer import FPLOptimizer


def main():
    print("="*80)
    print("FPL Optimizer - Basic Example")
    print("="*80)
    
    # Step 1: Fetch player data
    print("\n1. Fetching player data from FPL API...")
    client = FPLAPIClient()
    players_df = client.get_all_players()
    current_gw = client.get_current_gameweek()
    
    print(f"   ✓ Loaded {len(players_df)} players")
    print(f"   ✓ Current Gameweek: {current_gw}")
    
    # Step 2: Get player histories
    print("\n2. Fetching player performance histories...")
    player_ids = players_df['id'].tolist()
    histories = client.get_player_histories_bulk(player_ids[:50], current_gw)  # Limit to 50 for demo
    
    print(f"   ✓ Fetched history for {len(histories)} players")
    
    # Step 3: Estimate expected points using weighted average
    print("\n3. Calculating expected points (weighted average method)...")
    expected_points = estimate_expected_points(histories, method='weighted_average')
    
    # Filter players to only those we have history for
    players_df = players_df[players_df['id'].isin(expected_points.keys())]
    
    print(f"   ✓ Calculated expectations for {len(expected_points)} players")
    
    # Show top expected performers
    top_players = sorted(expected_points.items(), key=lambda x: x[1], reverse=True)[:5]
    print("\n   Top 5 Expected Performers:")
    for pid, pts in top_players:
        player = players_df[players_df['id'] == pid].iloc[0]
        print(f"     • {player['web_name']} ({player['position']}): {pts:.2f} pts")
    
    # Step 4: Run optimization
    print("\n4. Running integer programming optimization...")
    optimizer = FPLOptimizer(
        players_df=players_df,
        expected_points=expected_points,
        budget=83.5
    )
    
    solution = optimizer.solve()
    
    if solution:
        print("   ✓ Optimization successful!")
        
        # Step 5: Display results
        print("\n" + "="*80)
        print("OPTIMAL TEAM")
        print("="*80)
        optimizer.print_solution()
        
        # Show some statistics
        selected = solution['selected_players']
        print("\nTeam Statistics:")
        print(f"  • Formation: {solution['formation']}")
        print(f"  • Total Cost: £{solution['total_cost']:.1f}M")
        print(f"  • Expected Points: {solution['expected_points']:.2f}")
        print(f"  • Budget Remaining: £{solution['budget_remaining']:.1f}M")
        print(f"  • Teams represented: {selected['team_name'].nunique()}")
        
        # Position breakdown
        print("\n  Position breakdown:")
        for pos in ['GKP', 'DEF', 'MID', 'FWD']:
            pos_players = selected[selected['position'] == pos]
            avg_cost = pos_players['cost'].mean()
            total_exp = pos_players['expected_points'].sum()
            print(f"    {pos}: {len(pos_players)} players, "
                  f"Avg £{avg_cost:.1f}M, {total_exp:.1f} exp pts")
    else:
        print("   ✗ Optimization failed!")
    
    print("\n" + "="*80)
    print("Example completed!")
    print("="*80)


if __name__ == "__main__":
    main()
