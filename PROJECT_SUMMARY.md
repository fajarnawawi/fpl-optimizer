# FPL Optimizer - Project Summary

## ✅ Complete Repository Structure

```
fpl-optimizer/
├── README.md                    # Main documentation
├── QUICKSTART.md               # 5-minute getting started guide
├── METHODOLOGY.md              # Detailed mathematical documentation
├── LICENSE                     # MIT License
├── requirements.txt            # Python dependencies
├── setup.py                    # Package setup
├── .gitignore                  # Git ignore rules
│
├── src/                        # Main source code
│   ├── __init__.py
│   ├── config.py              # Configuration settings
│   ├── fpl_api.py             # FPL API client
│   ├── models.py              # Prediction models (7 methods)
│   ├── optimizer.py           # Integer programming optimizer
│   ├── main.py                # CLI entry point
│   └── utils.py               # Utility functions
│
├── data/                       # Data directory
│   ├── my_squad.json          # Your current squad (USER FILLS)
│   ├── player_history.json    # Auto-generated player data
│   └── gameweek_results.json  # Auto-generated results
│
├── tests/                      # Test suite
│   ├── __init__.py
│   └── test_optimizer.py      # Comprehensive tests
│
├── examples/                   # Usage examples
│   ├── basic_optimization.py  # Simple example
│   ├── compare_methods.py     # Compare all methods
│   └── weekly_automation.py   # Automated weekly run
│
└── scripts/                    # Automation scripts
    └── setup_cron.sh          # Cron job setup
```

## 🎯 Key Features Implemented

### 1. Integer Programming Optimization ✅
- Binary integer programming formulation
- All FPL constraints (formation, budget, team diversity)
- Automatic captain selection
- Budget: 83.5M for starting 11 (leaves 16.5M for reserves)

### 2. Seven Prediction Methods ✅
1. **Simple Average** - Basic baseline
2. **Weighted Average** ⭐ - Best consistent performer
3. **Exponential Smoothing** - Trend-based
4. **Monte Carlo Simulation** ⭐ - Best consistent performer
5. **ARIMA** - Time series forecasting
6. **Linear Regression** - Trend extrapolation
7. **Hybrid ML** 🏆 - Highest peak score (83 pts)

### 3. Robust Optimization ✅
- Box uncertainty formulation
- Worst-case scenario optimization
- Configurable uncertainty margins
- Risk-averse strategy option

### 4. Real-time FPL API Integration ✅
- Fetches live player data
- Historical performance tracking
- Current gameweek detection
- Fixture information

### 5. Transfer Recommendations ✅
- Suggests optimal transfers
- Considers budget constraints
- Position matching
- Expected points gain calculation

### 6. Automation Support ✅
- Weekly optimization script
- Cron job setup
- Results tracking
- JSON data persistence

## 📊 Performance (from Paper)

**Test Period:** Gameweeks 27-38, 2023/24 Season

| Method | Peak Score | Avg Consistency |
|--------|-----------|-----------------|
| Hybrid ML | 83 | ⭐⭐⭐ |
| Monte Carlo | 82 | ⭐⭐⭐⭐⭐ |
| Weighted Avg | 70 | ⭐⭐⭐⭐⭐ |
| ICT Index | 67 | ⭐⭐⭐ |
| Exp Smoothing | 77 | ⭐⭐ |
| ARIMA | 60 | ⭐⭐ |
| Linear Reg | 69 | ⭐⭐ |

## 🚀 Quick Usage

### Installation
```bash
cd fpl-optimizer
pip install -r requirements.txt
```

### Basic Usage
```bash
# 1. Set up your squad
python src/main.py --create-template
# (Edit data/my_squad.json)

# 2. Optimize
python src/main.py --method weighted_average

# 3. Get transfers
python src/main.py --suggest-transfers
```

### Compare Methods
```bash
python src/main.py --compare-all
```

### Automate
```bash
# Set up weekly automation
chmod +x scripts/setup_cron.sh
./scripts/setup_cron.sh
```

## 📦 Dependencies

**Core:**
- pulp >= 2.7.0 (Integer programming)
- pandas >= 2.0.0 (Data manipulation)
- numpy >= 1.24.0 (Numerical computing)
- requests >= 2.31.0 (API calls)

**ML & Statistics:**
- scikit-learn >= 1.3.0 (Ridge regression)
- scipy >= 1.11.0 (Statistical functions)
- statsmodels >= 0.14.0 (Time series)

**Optional:**
- matplotlib >= 3.7.0 (Visualization)
- pytest >= 7.4.0 (Testing)

## 🧪 Testing

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest --cov=src tests/

# Run integration tests only
pytest -m integration tests/
```

## 📖 Documentation

1. **README.md** - Overview, features, usage
2. **QUICKSTART.md** - 5-minute setup guide
3. **METHODOLOGY.md** - Mathematical details
4. **Docstrings** - Inline code documentation

## 🎓 Based on Research

**Paper:**  
Ramezani, D. (2025). "Data-Driven Team Selection in Fantasy Premier League Using Integer Programming and Predictive Modeling Approach."  
arXiv:2505.02170 [cs.CE]

**Key Contributions from Paper:**
- Novel integer programming formulation for FPL
- Comparison of 7 prediction methods
- Hybrid ML approach with SHAP-informed features
- Robust optimization variant
- Empirical validation on 2023/24 season

## 🔧 Customization Options

### Configuration (src/config.py)
- Budget allocation
- Formation constraints
- Uncertainty margins
- Simulation parameters
- ML model hyperparameters

### Custom Constraints
```python
from src.optimizer import FPLOptimizer

optimizer = FPLOptimizer(players_df, expected_points)

# Must include specific player
optimizer.add_must_include_constraint([player_id])

# Exclude injured player
optimizer.add_must_exclude_constraint([player_id])
```

### Custom Prediction Method
```python
from src.models import PredictionModels

# Add your own method
def my_custom_method(points_history):
    # Your logic here
    return expected_points

# Use in optimization
expected = {
    pid: my_custom_method(history)
    for pid, history in histories.items()
}
```

## 🐛 Known Limitations

1. **No Transfer Strategy** - Optimizes single gameweek only (no multi-week planning)
2. **No Special Cards** - Doesn't model bench boost, triple captain, etc.
3. **Static Captain** - Captain chosen once, not dynamically updated
4. **Reserve Selection** - Doesn't optimize bench (assumes 4 cheapest)
5. **No Fixture Difficulty** - Doesn't factor in upcoming fixture difficulty

## 🔮 Future Enhancements

**Potential additions:**
- [ ] Rolling horizon optimization for transfers
- [ ] Special cards modeling
- [ ] Dynamic captaincy
- [ ] Fixture difficulty integration
- [ ] Deep learning models (LSTM, Transformers)
- [ ] Web interface
- [ ] Mobile app
- [ ] Automatic FPL account integration
- [ ] Differential ownership analysis
- [ ] Expected value vs. Template analysis

## 💡 Usage Tips

1. **Method Selection:**
   - **Safe/Consistent:** Use `weighted_average` or `monte_carlo`
   - **High Risk/Reward:** Use `hybrid`
   - **Conservative:** Use `--robust` flag

2. **Squad Setup:**
   - Update `data/my_squad.json` weekly
   - Can use player names or IDs
   - Tool auto-matches names

3. **Transfer Strategy:**
   - Run `--suggest-transfers` before deadline
   - Consider expected points gain vs. cost
   - Factor in fixtures manually

4. **Captain Selection:**
   - Tool auto-selects based on expected points
   - Consider ceiling vs. floor manually
   - Popular vs. differential choice

5. **Formation:**
   - 3-5-2 most commonly optimal
   - Midfielders often best value
   - Don't force formation preferences

## 📞 Support

- **Issues:** Open a GitHub issue
- **Questions:** Check QUICKSTART.md and METHODOLOGY.md
- **Paper:** https://arxiv.org/abs/2505.02170
- **FPL API:** https://fantasy.premierleague.com/api/

## ⚖️ License

MIT License - See LICENSE file

## ⚠️ Disclaimer

Educational and research purposes only. FPL outcomes depend on unpredictable real-world football. Past performance doesn't guarantee future results. Always use your own judgment.

---

## 🎉 Ready to Use!

Your FPL Optimizer is complete and ready to help you climb the rankings!

**Next Steps:**
1. Read QUICKSTART.md
2. Set up your squad in data/my_squad.json
3. Run your first optimization
4. Dominate your mini-leagues! 🏆

**May your captain always haul!** ⚽🎯

---

**Project Version:** 1.0.0  
**Created:** 2025-01-18  
**Based on:** arXiv:2505.02170
