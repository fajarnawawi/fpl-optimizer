# Quick Start Guide 🚀

Get your optimal FPL team in 5 minutes!

## Step 1: Installation

```bash
cd fpl-optimizer
pip install -r requirements.txt
```

## Step 2: Set Up Your Squad

Edit `data/my_squad.json` with your current FPL squad:

```bash
# You can use the template or create from scratch
python src/main.py --create-template
```

Then edit the file with your 15 players. You can use either:
- Player IDs from the FPL API
- Player names (the tool will match them automatically)

**Example:**
```json
{
  "squad": [
    {
      "name": "Raya",
      "position": "GKP",
      "team": "Arsenal"
    },
    {
      "name": "Saliba",
      "position": "DEF",
      "team": "Arsenal"
    },
    ...
  ],
  "budget": 0.5,
  "free_transfers": 1
}
```

## Step 3: Run Your First Optimization

```bash
# Optimize with weighted average (recommended)
python src/main.py --method weighted_average
```

That's it! You'll see your optimal starting 11 and captain selection.

## Common Use Cases

### 1. Quick Optimization (Recommended Methods)

```bash
# Weighted Average - Most consistent performer
python src/main.py --method weighted_average

# Monte Carlo - Also very consistent
python src/main.py --method monte_carlo

# Hybrid ML - Highest peak performance
python src/main.py --method hybrid
```

### 2. Compare All Methods

```bash
python src/main.py --compare-all
```

This will run all 7 prediction methods and show you a comparison table.

### 3. Get Transfer Recommendations

```bash
# Get 1 transfer suggestion
python src/main.py --suggest-transfers

# Get up to 2 transfer suggestions
python src/main.py --suggest-transfers --max-transfers 2
```

### 4. Optimize Without Squad Constraint

If you want to see the absolute optimal team from ALL players (not just your current squad):

```bash
python src/main.py --method weighted_average --no-squad-constraint
```

### 5. Use Robust Optimization (Risk-Averse)

For a more conservative strategy that maximizes worst-case performance:

```bash
python src/main.py --method weighted_average --robust
```

### 6. Optimize for a Specific Gameweek

```bash
# Optimize for gameweek 30
python src/main.py --method weighted_average --gameweek 30
```

## Understanding the Output

The optimizer will show you:

```
================================================================================
FPL OPTIMAL TEAM - 3-5-2 Formation
================================================================================
GKP  | Raya                 | Arsenal        | £5.3M | Exp: 4.5 pts
DEF  | Saliba               | Arsenal        | £5.7M | Exp: 5.2 pts
DEF  | Gabriel              | Arsenal        | £5.2M | Exp: 4.8 pts
DEF  | Trippier             | Newcastle      | £6.9M | Exp: 4.9 pts
MID  | Saka                 | Arsenal        | £9.1M | Exp: 7.8 pts (C)
MID  | Foden                | Man City       | £8.1M | Exp: 7.2 pts
MID  | Palmer               | Chelsea        | £5.8M | Exp: 6.5 pts
MID  | Salah                | Liverpool      | £13.0M| Exp: 8.9 pts
MID  | Douglas Luiz         | Aston Villa    | £5.5M | Exp: 4.7 pts
FWD  | Watkins              | Aston Villa    | £8.8M | Exp: 7.1 pts
FWD  | Solanke              | Bournemouth    | £7.0M | Exp: 5.8 pts
--------------------------------------------------------------------------------
Total Cost: £81.4M (Remaining: £2.1M)
Expected Points: 73.2
================================================================================

(C) = Captain (gets double points)
```

## Results Tracking

All your optimization results are automatically saved to `data/gameweek_results.json`.

You can track:
- Which formation was optimal
- Which players were selected
- Expected vs actual points (you can update this manually)
- Performance across different methods

## Tips for Best Results

1. **Update Your Squad Regularly**: Before each gameweek, update `data/my_squad.json` with any transfers you made.

2. **Try Multiple Methods**: Use `--compare-all` to see which method suits your style. Weighted average and Monte Carlo are most consistent.

3. **Check Transfer Suggestions**: Even if you don't follow them, `--suggest-transfers` gives you data-driven insights.

4. **Consider Form**: The weighted average method automatically weighs recent performance more heavily.

5. **Budget Management**: The optimizer leaves ~£2M buffer for your reserves. Adjust `STARTING_11_BUDGET` in `src/config.py` if needed.

## Troubleshooting

**Problem**: "No squad found"
- **Solution**: Make sure `data/my_squad.json` exists and has valid player data

**Problem**: "Optimization failed"
- **Solution**: Check your budget and squad composition. You need at least 15 valid players.

**Problem**: "Player name not found"
- **Solution**: Use exact player names from FPL (web_name). Check the FPL API for correct names.

**Problem**: Method takes too long
- **Solution**: 
  - Monte Carlo: It runs 1000 simulations (can reduce in config)
  - ARIMA: Can be slow with many players
  - Try weighted_average for faster results

## Advanced Usage

See the main `README.md` for:
- Programmatic usage with Python
- Custom constraints
- Robust optimization details
- Hybrid ML model explanation

## Need Help?

- Check the main README.md
- Open an issue on GitHub
- Review the paper: https://arxiv.org/abs/2505.02170

---

Happy optimizing! May your captain always haul! 🎯⚽
