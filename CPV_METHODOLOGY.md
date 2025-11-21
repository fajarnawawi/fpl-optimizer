# Composite Player Viability (CPV) Score Methodology

## Overview

The CPV Score is a unified framework for player evaluation that combines quantitative predictions with contextual factors. This methodology addresses the limitations of using raw expected points (xP) alone by incorporating fixture difficulty, player form, value metrics, and injury status.

## CPV Formula

```
CPV = (W_xP × xP_norm + W_FFI × FFI + W_VCS × VCS) × SSS
```

Where:
- **W_xP = 0.40** (40% weight) - Predicted Points
- **W_FFI = 0.25** (25% weight) - Fixture & Form Index
- **W_VCS = 0.15** (15% weight) - Value & Ceiling Score
- **W_SSS = 0.20** (20% weight) - Sentiment & Status Signal (used as multiplier)

## Components

### 1. Predicted Points (xP) - 40%
Normalized expected points from the base prediction model (weighted average, Monte Carlo, ARIMA, etc.)

### 2. Fixture & Form Index (FFI) - 25%
Position-dependent weighting of fixture difficulty and recent form:

**For Defenders/Goalkeepers:**
```
FFI = 0.7 × Fixture_Score + 0.3 × Form_Score
```
Rationale: Clean sheets (fixture-dependent) are primary scoring mechanism

**For Midfielders/Forwards:**
```
FFI = 0.3 × Fixture_Score + 0.7 × Form_Score
```
Rationale: Goals/assists (form-dependent) are primary scoring mechanism

Where:
- **Fixture_Score** = (5 - FDR) / 4.0 (normalized 0-1, lower FDR = better)
- **Form_Score** = Form / 10.0 (normalized 0-1)

### 3. Value & Ceiling Score (VCS) - 15%
Balances efficiency with explosive potential:

```
VCS = 0.5 × Value_Score + 0.5 × Ceiling_Score
```

Where:
- **Value_Score** = min(1.0, Points_Per_Million / 25.0)
- **Ceiling_Score** = min(1.0, ICT_Index / 300.0)

### 4. Sentiment & Status Signal (SSS) - 20%
Non-linear veto mechanism for injury/availability:

```
SSS = {
    0.0           if chance < 75%    (VETO)
    chance/100    if 75% ≤ chance < 100%
    1.0           if chance is None (100% assumed)
}
```

This prevents selection of doubtful players regardless of high xP.

## Strategic Overlays

After calculating base CPV scores, strategic adjustments can be applied based on ownership (EO):

### Standard Strategy
```
Final_Score = CPV
```
Pure point maximization

### Rank Protection Strategy
```
Final_Score = CPV × (1 + 0.5 × EO)
```
Boosts high-ownership players to minimize variance and protect rank

### Rank Climbing Strategy
```
Final_Score = CPV × (1 + (1 - EO))
```
Favors differentials (low ownership) to maximize upside and climb ranks

## Usage Examples

```bash
# Standard optimization with CPV
python main.py --method weighted_average

# Find differentials to climb mini-league
python main.py --method weighted_average --strategy rank_climbing

# Protect top rank by following the crowd
python main.py --method weighted_average --strategy rank_protection

# Combine with robust optimization
python main.py --method monte_carlo --strategy rank_climbing --robust
```

## Key Benefits

1. **Position Intelligence**: Defenders evaluated on fixtures, attackers on form
2. **Injury Protection**: Automatic veto of unavailable players
3. **Value Optimization**: Balances efficiency with ceiling potential
4. **Game Theory**: Strategic modes for different competitive situations

## Implementation Files

- `src/cpv.py` - CPVCalculator class
- `src/strategies.py` - StrategyOverlay class
- `src/fpl_api.py` - get_next_fixture_difficulty() method
- `src/main.py` - Integration and CLI

## References

Based on "FPL Squad and Transfer Methodology" combining:
- Predictive modeling (xP from various methods)
- Fixture analysis (FDR ratings)
- Form metrics (recent performance)
- Value metrics (PPM, ICT index)
- Status signals (injury/availability)
