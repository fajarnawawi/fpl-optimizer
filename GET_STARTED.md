# 🚀 FPL Optimizer - Getting Started NOW

## ⚡ 3-Minute Setup

### Step 1: Install (30 seconds)
```bash
cd fpl-optimizer
pip install -r requirements.txt
```

### Step 2: Create Squad File (1 minute)
```bash
python src/main.py --create-template
```

Edit `data/my_squad.json` - Just add your player names:
```json
{
  "squad": [
    {"name": "Raya", "position": "GKP"},
    {"name": "Saliba", "position": "DEF"},
    {"name": "Gabriel", "position": "DEF"},
    ... (add all 15 players)
  ],
  "budget": 0.5,
  "free_transfers": 1
}
```

### Step 3: Run (30 seconds)
```bash
python src/main.py --method weighted_average
```

**DONE!** 🎉 You'll see your optimal starting 11 and captain!

---

## 🎯 What You Get

```
================================================================================
FPL OPTIMAL TEAM - 3-5-2 Formation
================================================================================
GKP  | Raya                 | Arsenal        | £5.3M | Exp: 4.5 pts
DEF  | Saliba               | Arsenal        | £5.7M | Exp: 5.2 pts
DEF  | Gabriel              | Arsenal        | £5.2M | Exp: 4.8 pts
DEF  | Trippier             | Newcastle      | £6.9M | Exp: 4.9 pts
MID  | Saka                 | Arsenal        | £9.1M | Exp: 7.8 pts (C) ⭐
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
```

---

## 🔥 Common Commands

```bash
# Basic optimization (recommended method)
python src/main.py --method weighted_average

# Try Monte Carlo (also excellent)
python src/main.py --method monte_carlo

# Highest risk/reward
python src/main.py --method hybrid

# Compare ALL methods
python src/main.py --compare-all

# Get transfer suggestions
python src/main.py --suggest-transfers

# Optimize from ALL players (not just your squad)
python src/main.py --no-squad-constraint

# Use robust optimization (conservative)
python src/main.py --robust
```

---

## 📊 Which Method Should I Use?

| If you want... | Use this method | Command |
|----------------|-----------------|---------|
| **Most consistent** | Weighted Average | `--method weighted_average` |
| **Also very consistent** | Monte Carlo | `--method monte_carlo` |
| **Highest ceiling** | Hybrid ML | `--method hybrid` |
| **Risk-averse** | Any + Robust | `--method weighted_average --robust` |
| **See everything** | Compare All | `--compare-all` |

**Recommendation:** Start with `weighted_average` - it's the most reliable!

---

## 🎓 Understanding the Output

### Expected Points
- Based on historical performance
- Weighted toward recent form
- Captain gets DOUBLE points (marked with (C))

### Formation
- Most common: **3-5-2** (3 defenders, 5 midfielders, 2 forwards)
- Midfielders typically offer best value
- Tool automatically finds optimal balance

### Budget
- Tool uses 83.5M of your 100M budget
- Leaves 16.5M for 4 bench players
- Assumes cheapest bench players (£4-4.5M each)

---

## 💡 Pro Tips

### 1. Update Your Squad Weekly
Before each gameweek:
```bash
# Edit data/my_squad.json with any transfers you made
python src/main.py
```

### 2. Check Transfer Suggestions
```bash
python src/main.py --suggest-transfers --max-transfers 2
```
- Shows which players to swap
- Calculates expected points gain
- Considers your budget

### 3. Compare Methods for Big Decisions
```bash
python src/main.py --compare-all
```
If multiple methods agree = strong signal!

### 4. Use for Differentials
```bash
python src/main.py --no-squad-constraint
```
See the absolute optimal team (might be very different from yours)

### 5. Captain Selection
The tool auto-picks captain based on expected points.
- Usually = highest expected points
- Consider: ceiling vs floor
- Consider: ownership% for differentials

---

## 🤔 Troubleshooting

**"No squad found"**
→ Create `data/my_squad.json` using `--create-template`

**"Player not found"**
→ Use exact FPL names (check FPL website)
→ Or use player ID numbers

**"Optimization failed"**
→ Check you have 15 valid players
→ Check budget allows a valid team

**Method takes too long**
→ ARIMA and Monte Carlo are slowest
→ Use `weighted_average` for speed

**Want more details**
→ Read `METHODOLOGY.md` for the math
→ Read `README.md` for full features
→ Check `examples/` for code samples

---

## 📅 Weekly Workflow

### Before Deadline (15 minutes)

1. **Update Squad** (2 min)
   ```bash
   # Edit data/my_squad.json if you made transfers
   ```

2. **Run Optimization** (2 min)
   ```bash
   python src/main.py --method weighted_average
   ```

3. **Check Transfers** (5 min)
   ```bash
   python src/main.py --suggest-transfers
   ```

4. **Set Team** (5 min)
   - Go to FPL website
   - Set your starting 11 (from step 2)
   - Set captain (from step 2)
   - Consider transfers (from step 3)

5. **Done!** ✅

### Optional: Automate It
```bash
chmod +x scripts/setup_cron.sh
./scripts/setup_cron.sh
```
Runs automatically every Friday before deadline!

---

## 🎯 Success Metrics

From the research paper (GW27-38, 2023/24):

- **Hybrid:** 83 points (best single week)
- **Monte Carlo:** 82 points 
- **Weighted Avg:** 70 points (most consistent)

**Your mileage may vary** - football is unpredictable! But this gives you a data-driven edge.

---

## 🏆 Next Steps

1. ✅ **You're set up!** Run your first optimization
2. 📖 Read `QUICKSTART.md` for more details
3. 🧮 Read `METHODOLOGY.md` to understand the math
4. 🤖 Set up automation with `scripts/setup_cron.sh`
5. 📊 Track your results vs. the model

---

## 💬 Questions?

- Check `README.md` for full documentation
- Check `PROJECT_SUMMARY.md` for complete overview
- Read the paper: https://arxiv.org/abs/2505.02170
- Open a GitHub issue for bugs/questions

---

## 🎉 Ready to Dominate!

You now have a sophisticated, research-backed FPL optimization tool.

**Remember:**
- No model is perfect
- Football is unpredictable
- Use this as ONE input to your decisions
- Have fun and may your captain always haul! ⚽🏆

---

**GO GET 'EM!** 💪
