# FPL Optimizer 🏆⚽

An intelligent Fantasy Premier League (FPL) optimization agent based on the research paper:
**"Data-Driven Team Selection in Fantasy Premier League Using Integer Programming and Predictive Modeling Approach"** by Danial Ramezani.

## 📋 Overview

This tool automatically selects your optimal FPL starting 11 and captain for each gameweek using:
- **Integer Programming** for constraint-based optimization
- **Multiple Prediction Models** (Weighted Average, Monte Carlo, Hybrid ML approach)
- **Robust Optimization** techniques
- **Real-time FPL API** data integration

## 🎯 Features

- ✅ Fetch live player data from FPL API
- ✅ Multiple cost estimation methods (as per paper):
  - Weighted Average (best performing in paper)
  - Monte Carlo Simulation (best performing in paper)
  - Exponential Smoothing
  - ARIMA forecasting
  - Linear Regression
  - **Hybrid ML approach** with explainable AI
- ✅ Integer Programming optimization with budget/formation constraints
- ✅ Automatic captain selection
- ✅ Transfer recommendations
- ✅ Gameweek-by-gameweek automation

## 🚀 Quick Start

### Installation

```bash
# Clone repository
cd fpl-optimizer

# Install dependencies
pip install -r requirements.txt
```

### Initial Setup

1. **Set up your current squad** in `data/my_squad.json`:

```json
{
  "squad": [
    {"id": 1, "name": "Player Name", "position": "GKP", "team": "Arsenal", "cost": 4.5},
    ...
  ],
  "budget": 0.5,
  "free_transfers": 1
}
```

2. **Run the optimizer**:

```bash
# For current gameweek with weighted average method (recommended)
python src/main.py --method weighted_average

# For Monte Carlo simulation (also excellent performance)
python src/main.py --method monte_carlo

# For hybrid ML approach (highest single gameweek score in paper)
python src/main.py --method hybrid

# For all methods comparison
python src/main.py --compare-all
```

## 📊 Methods Comparison (from paper)

Based on the 2023/24 Premier League season evaluation (gameweeks 27-38):

| Method | Best Score | Consistency | Formation Preference |
|--------|-----------|-------------|---------------------|
| **Hybrid ML** | **83** (GW27) | Medium | 3-5-2 |
| **Monte Carlo** | **82** (GW27) | **High** | 3-5-2 |
| **Weighted Average** | 70 | **Very High** | 3-5-2 |
| ICT Index | 67 | Medium | 3-5-2 |
| Exponential Smoothing | 77 | Low | 3-5-2 |
| ARIMA | 60 | Low | 5-4-1 |
| Linear Regression | 69 | Low | 3-4-3 |

**Recommendation**: Use `weighted_average` or `monte_carlo` for consistent performance.

## 🔧 Configuration

Edit `config.py` to customize:
- Budget allocation
- Risk tolerance for robust optimization
- Simulation parameters (for Monte Carlo)
- ML model parameters (for Hybrid approach)

## 📖 Usage Examples

### Basic Usage
```python
from src.optimizer import FPLOptimizer

# Initialize optimizer
optimizer = FPLOptimizer(method='weighted_average')

# Get recommendations for current gameweek
recommendations = optimizer.optimize_team()

print(f"Starting 11: {recommendations['starting_11']}")
print(f"Captain: {recommendations['captain']}")
print(f"Expected Points: {recommendations['expected_points']}")
```

### Transfer Recommendations
```python
# Get transfer suggestions
transfers = optimizer.suggest_transfers(max_transfers=1)
print(f"Suggested Transfers: {transfers}")
```

### Multiple Methods Comparison
```python
# Compare all methods
results = optimizer.compare_methods()
for method, result in results.items():
    print(f"{method}: {result['expected_points']} pts")
```

## 📁 Project Structure

```
fpl-optimizer/
├── src/
│   ├── __init__.py
│   ├── main.py              # Main entry point
│   ├── config.py            # Configuration settings
│   ├── fpl_api.py           # FPL API data fetcher
│   ├── models.py            # Prediction models (all methods)
│   ├── optimizer.py         # Integer programming optimization
│   ├── captain_selector.py  # Captain selection logic
│   └── utils.py             # Utility functions
├── data/
│   ├── my_squad.json        # Your current squad (you define this)
│   ├── player_history.json  # Historical player data (auto-generated)
│   └── gameweek_results.json # Results tracking (auto-generated)
├── requirements.txt
├── README.md
└── setup.py
```

## 🧮 Methodology

### Integer Programming Model

The optimizer uses a binary integer programming formulation:

**Decision Variables:**
- `x[j]` = 1 if player j is selected, 0 otherwise
- `y[j]` = 1 if player j is captain, 0 otherwise

**Objective:**
Maximize: Σ(c[j] × x[j]) + Σ(c[j] × y[j])

Where c[j] is the expected points for player j.

**Constraints:**
- Exactly 11 players selected
- Budget ≤ 83.5M (allows 16.5M for reserves)
- Exactly 1 captain
- Formation: 1 GK, 3-5 DEF, 3-5 MID, 1-3 FWD
- Max 3 players per Premier League team

### Prediction Methods

#### 1. Weighted Average (Recommended)
Gives more weight to recent gameweeks:
```
weight[i] = i / Σ(j=1 to N) j
expected_points = Σ(weight[i] × points[i])
```

#### 2. Monte Carlo Simulation (Recommended)
Runs 1000 simulations sampling from historical performance distribution.

#### 3. Hybrid ML (Highest Peak Performance)
- Uses XGBoost to predict based on underlying features (ICT, expected goals, etc.)
- Combines actual points with ML predictions
- Weight: 2:1 in favor of actual points

## ⚙️ Advanced Features

### Robust Optimization

For risk-averse strategies, enable robust optimization:

```python
optimizer = FPLOptimizer(
    method='weighted_average',
    robust=True,
    uncertainty_margin=0.2  # 20% uncertainty
)
```

This maximizes the worst-case scenario points.

### Custom Constraints

Add custom constraints like "must include Player X":

```python
optimizer.add_constraint(player_id=123, must_include=True)
```

## 📈 Performance Tracking

The tool automatically tracks:
- Gameweek-by-gameweek results
- Method performance comparison
- Captain success rate
- Transfer impact

View results in `data/gameweek_results.json`.

## 🔬 Research Paper Implementation

This implementation is based on:

> Ramezani, D. (2025). "Data-Driven Team Selection in Fantasy Premier League Using Integer Programming and Predictive Modeling Approach." arXiv:2505.02170

Key findings implemented:
1. ✅ 3-5-2 formation is most effective
2. ✅ Weighted average and Monte Carlo are most consistent
3. ✅ Hybrid approach achieves highest peaks but with more variance
4. ✅ Expensive forwards (Salah, Haaland) may not always be optimal

## 🤝 Contributing

Contributions welcome! Areas for improvement:
- Additional prediction models
- Dynamic transfer strategies
- Special cards optimization (bench boost, triple captain, etc.)
- Web interface
- Integration with FPL accounts for automatic team updates

## 📄 License

MIT License - See LICENSE file

## ⚠️ Disclaimer

This tool is for educational and research purposes. Fantasy Premier League outcomes depend on real-world football performance which is inherently unpredictable. Past performance does not guarantee future results. Always use your own judgment when making FPL decisions.

## 📧 Contact

For questions or suggestions, please open an issue on GitHub.

---

**Made with ⚽ and 🤖 by FPL enthusiasts**
