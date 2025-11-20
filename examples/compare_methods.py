"""
Example: Compare All Prediction Methods
Shows performance differences between methods
"""

import sys
sys.path.insert(0, '../src')

from fpl_api import FPLAPIClient
from models import estimate_expected_points, HybridModel
from optimizer import FPLOptimizer
import pandas as pd


def compare_methods():
    """Compare all prediction methods"""
    
    print("="*80)
    print("FPL Optimizer - Method Comparison")
    print("="*80)
    
    # Fetch data
    print("\nFetching player data...")
    client = FPLAPIClient()
    players_df = client.get_all_players()
    current_gw = client.get_current_gameweek()
    
    # Get histories
    print("Fetching player histories...")
    player_ids = players_df['id'].tolist()[:100]  # Limit for demo
    histories = client.get_player_histories_bulk(player_ids, current_gw)
    
    # Filter to players with history
    players_df = players_df[players_df['id'].isin(histories.keys())]
    
    methods = [
        'simple_average',
        'weighted_average',
        'exponential_smoothing',
        'monte_carlo',
        'arima',
        'linear_regression'
    ]
    
    results = {}
    
    for method in methods:
        print(f"\n{'='*80}")
        print(f"Testing: {method.replace('_', ' ').title()}")
        print(f"{'='*80}")
        
        try:
            # Calculate expected points
            expected_points = estimate_expected_points(
                histories, 
                method=method,
                weeks_to_end=38-current_gw
            )
            
            # Run optimization
            optimizer = FPLOptimizer(
                players_df=players_df,
                expected_points=expected_points,
                budget=83.5
            )
            
            solution = optimizer.solve()
            
            if solution:
                results[method] = {
                    'formation': solution['formation'],
                    'expected_points': solution['expected_points'],
                    'total_cost': solution['total_cost'],
                    'captain': solution['selected_players'][
                        solution['selected_players']['is_captain']
                    ]['web_name'].values[0]
                }
                
                print(f"✓ Formation: {solution['formation']}")
                print(f"✓ Expected Points: {solution['expected_points']:.2f}")
                print(f"✓ Captain: {results[method]['captain']}")
            else:
                print(f"✗ Optimization failed")
                
        except Exception as e:
            print(f"✗ Error: {e}")
            continue
    
    # Test hybrid method
    print(f"\n{'='*80}")
    print(f"Testing: Hybrid ML Approach")
    print(f"{'='*80}")
    
    try:
        hybrid_model = HybridModel()
        hybrid_model.fit(players_df)
        expected_points_series = hybrid_model.hybrid_score(
            players_df,
            players_df['total_points']
        )
        expected_points = expected_points_series.to_dict()
        
        optimizer = FPLOptimizer(
            players_df=players_df,
            expected_points=expected_points,
            budget=83.5
        )
        
        solution = optimizer.solve()
        
        if solution:
            results['hybrid'] = {
                'formation': solution['formation'],
                'expected_points': solution['expected_points'],
                'total_cost': solution['total_cost'],
                'captain': solution['selected_players'][
                    solution['selected_players']['is_captain']
                ]['web_name'].values[0]
            }
            
            print(f"✓ Formation: {solution['formation']}")
            print(f"✓ Expected Points: {solution['expected_points']:.2f}")
            print(f"✓ Captain: {results['hybrid']['captain']}")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Print comparison table
    print("\n" + "="*80)
    print("RESULTS SUMMARY")
    print("="*80)
    
    # Create comparison DataFrame
    comparison_df = pd.DataFrame(results).T
    comparison_df = comparison_df.sort_values('expected_points', ascending=False)
    
    print(f"\n{'Method':<25} | {'Formation':<10} | {'Exp Points':<12} | {'Cost':<10} | {'Captain':<15}")
    print("-"*80)
    
    for method, row in comparison_df.iterrows():
        print(f"{method.replace('_', ' ').title():<25} | "
              f"{row['formation']:<10} | "
              f"{row['expected_points']:>12.2f} | "
              f"£{row['total_cost']:>7.1f}M | "
              f"{row['captain']:<15}")
    
    print("\n" + "="*80)
    
    # Analysis
    print("\nAnalysis:")
    best_method = comparison_df.index[0]
    best_score = comparison_df.iloc[0]['expected_points']
    worst_score = comparison_df.iloc[-1]['expected_points']
    
    print(f"  • Best Method: {best_method.replace('_', ' ').title()} ({best_score:.2f} pts)")
    print(f"  • Score Range: {worst_score:.2f} - {best_score:.2f} pts")
    print(f"  • Difference: {best_score - worst_score:.2f} pts")
    
    # Formation analysis
    formations = comparison_df['formation'].value_counts()
    print(f"\n  Most common formation: {formations.index[0]} ({formations.values[0]} methods)")
    
    print("\n" + "="*80)


if __name__ == "__main__":
    compare_methods()
