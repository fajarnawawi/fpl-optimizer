# FPL Optimizer - Methodology Documentation

This document provides detailed information about the mathematical models and algorithms used in this optimizer, based on the research paper by Danial Ramezani.

## Table of Contents
1. [Integer Programming Formulation](#integer-programming-formulation)
2. [Prediction Methods](#prediction-methods)
3. [Robust Optimization](#robust-optimization)
4. [Hybrid ML Approach](#hybrid-ml-approach)
5. [Performance Analysis](#performance-analysis)

---

## Integer Programming Formulation

The team selection problem is formulated as a binary integer programming problem.

### Decision Variables

- **x[j] ∈ {0, 1}**: Binary variable where x[j] = 1 if player j is selected in the starting 11, else 0
- **y[j] ∈ {0, 1}**: Binary variable where y[j] = 1 if player j is selected as captain, else 0

### Parameters

- **n**: Total number of available players
- **c[j]**: Expected points for player j (estimated using various methods)
- **b**: Total budget (83.5M for starting 11)
- **v[j]**: Cost (value) of player j
- **Team[t]**: Set of players belonging to team t
- **Position[k]**: Set of players in position k (GKP, DEF, MID, FWD)

### Objective Function

**Maximize:**
```
Z = Σ(j=1 to n) c[j] × x[j] + Σ(j=1 to n) c[j] × y[j]
```

This maximizes total expected points, where the captain gets double points.

### Constraints

1. **Squad Size**: Exactly 11 players selected
   ```
   Σ(j=1 to n) x[j] = 11
   ```

2. **Budget**: Total cost within budget
   ```
   Σ(j=1 to n) v[j] × x[j] ≤ b
   ```

3. **Captain Selection**: Exactly one captain
   ```
   Σ(j=1 to n) y[j] = 1
   ```

4. **Captain Must Be Selected**: Captain must be in starting 11
   ```
   y[j] ≤ x[j], ∀j = 1, 2, ..., n
   ```

5. **Formation Constraints**: Valid FPL formation
   - Goalkeepers: 1 GKP
   - Defenders: 3-5 DEF
   - Midfielders: 3-5 MID
   - Forwards: 1-3 FWD
   
   ```
   Σ(j∈GKP) x[j] = 1
   3 ≤ Σ(j∈DEF) x[j] ≤ 5
   3 ≤ Σ(j∈MID) x[j] ≤ 5
   1 ≤ Σ(j∈FWD) x[j] ≤ 3
   ```

6. **Team Diversity**: Max 3 players from any single team
   ```
   Σ(j∈Team[t]) x[j] ≤ 3, ∀t = 1, 2, ..., 20
   ```

---

## Prediction Methods

Different methods for estimating c[j] (expected points):

### 1. Simple Average

**Formula:**
```
c[j] = (1/N) × Σ(i=1 to N) p[i]
```

Where:
- N = number of gameweeks
- p[i] = points scored in gameweek i

**Characteristics:**
- Treats all gameweeks equally
- Simple and stable
- May miss recent form changes

### 2. Weighted Average (Recommended)

**Formula:**
```
w[i] = i / Σ(k=1 to N) k

c[j] = Σ(i=1 to N) w[i] × p[i]
```

**Characteristics:**
- Recent performances weighted more heavily
- Weight increases linearly with recency
- **Best consistent performer in paper** (tied with Monte Carlo)

### 3. Exponential Smoothing

**Holt-Winters Additive Model:**
```
ℓ[t] = α × p[t] + (1 - α) × (ℓ[t-1] + b[t-1])
b[t] = β × (ℓ[t] - ℓ[t-1]) + (1 - β) × b[t-1]
p̂[t] = ℓ[t-1] + b[t-1]
```

Where:
- ℓ[t] = level at time t
- b[t] = trend at time t
- α, β = smoothing parameters

**Characteristics:**
- Captures trend in performance
- Good for players with improving/declining form
- Can be unstable with volatile data

### 4. Monte Carlo Simulation (Recommended)

**Algorithm:**
```
For i = 1 to N_simulations:
    Sample p̂[i] randomly from historical points {p[1], ..., p[N]}
    
c[j] = mean(p̂[1], ..., p̂[N_simulations])
```

**Default:** N_simulations = 1000

**Characteristics:**
- Non-parametric approach
- Captures distribution of performance
- **Best consistent performer in paper** (tied with Weighted Average)
- Robust to outliers

### 5. ARIMA Forecasting

**ARIMA(p, d, q) Model:**
```
ϕ(B) × (1 - B)^d × p[t] = θ(B) × ε[t]
```

Where:
- B = backshift operator
- d = order of differencing
- ϕ(B) = autoregressive polynomial
- θ(B) = moving average polynomial
- ε[t] = white noise

**Characteristics:**
- Time series forecasting approach
- Good for structured patterns
- Can be unstable with short histories
- More computationally intensive

### 6. Linear Regression

**Model:**
```
p[i] = β₀ + β₁ × week[i] + ε[i]

c[j] = mean(β₀ + β₁ × week[future])
```

**Characteristics:**
- Assumes linear trend
- Simple and fast
- May not capture non-linear patterns

### 7. Hybrid ML Approach (Highest Peak)

**Combines Ridge Regression with actual points:**

```
# For each position, fit Ridge regression:
y_pred = Ridge(α=1.0).fit(X, y).predict(X)

# Normalize:
y_norm = (y - y_min) / (y_max - y_min)
y_pred_norm = (y_pred - y_pred_min) / (y_pred_max - y_pred_min)

# Combine with 2:1 ratio:
c[j] = (2 × y_norm + 1 × y_pred_norm) / 3

# Scale back:
c[j] = c[j] × (y_max - y_min) + y_min
```

**Features used (from SHAP analysis):**
- ICT Index
- Influence
- Creativity
- Threat
- Expected Goals (xG)
- Expected Assists (xA)
- Expected Goal Involvements (xGI)
- Expected Goals Conceded (xGC)
- Starts

**Characteristics:**
- **Highest single gameweek score (83 pts in GW27)**
- Uses underlying performance metrics
- More variance than other methods
- Position-specific models

---

## Robust Optimization

For risk-averse strategies, the robust formulation maximizes worst-case performance:

### Box Uncertainty Set

```
U = {c ∈ ℝⁿ : c[j] ∈ [c̄[j] - d[j], c̄[j] + d[j]], ∀j}
```

Where:
- c̄[j] = nominal expected score
- d[j] = uncertainty margin (e.g., 15% of c̄[j])

### Robust Objective

**Maximize the worst-case:**
```
max(x,y) min(c∈U) Σ(j=1 to n) c[j] × (x[j] + y[j])
```

**Equivalent formulation:**
```
max Σ(j=1 to n) (c̄[j] - d[j]) × (x[j] + y[j])
```

**Characteristics:**
- Conservative approach
- Protects against overestimation
- Lower expected points but more stable
- Good for risk-averse managers

---

## Performance Analysis

### Results from Paper (2023/24 Season, GW27-38)

| Method | Best Score | Consistency | Formation |
|--------|-----------|-------------|-----------|
| **Hybrid ML** | **83** | Medium | 3-5-2 |
| **Monte Carlo** | **82** | **High** | 3-5-2 |
| **Weighted Average** | 70 | **Very High** | 3-5-2 |
| ICT Index | 67 | Medium | 3-5-2 |
| Exponential Smoothing | 77 | Low | 3-5-2 |
| ARIMA | 60 | Low | 5-4-1 |
| Linear Regression | 69 | Low | 3-4-3 |

### Key Findings

1. **3-5-2 Formation Dominates**
   - Most methods selected 3-5-2
   - Midfielders provide best value
   - Only ARIMA chose defensive 5-4-1

2. **Weighted Average + Monte Carlo Most Reliable**
   - Consistent performance across gameweeks
   - Outperformed others in 5+ gameweeks each
   - Recommended for regular use

3. **Hybrid Achieves Highest Peaks**
   - GW27: 83 points (highest in study)
   - More variance week-to-week
   - Good for differential strategies

4. **Robust Optimization Mixed Results**
   - Generally underperformed deterministic versions
   - Exception: Robust ICT competitive with deterministic
   - Best for very risk-averse managers

5. **Captain Selection Patterns**
   - 3-5-2 formations: High-scoring midfielders/forwards
   - Other formations: Sometimes defenders (!

)
   - Bukayo Saka most frequently selected

6. **Player Selection Insights**
   - Ollie Watkins selected in ALL optimal teams
   - Arsenal defenders (Saliba, Gabriel) frequently chosen
   - Phil Foden and Bukayo Saka consistent picks
   - Salah/Haaland often too expensive for optimal balance

---

## Implementation Notes

### Solver
- Uses PuLP with CBC solver (open-source)
- Typically solves in < 1 second
- Handles up to ~700 players efficiently

### Computational Complexity
- **Deterministic IP**: O(n) variables, O(m) constraints
- **Robust IP**: Same complexity, just different coefficients
- **Monte Carlo**: O(N_sim × n) for prediction
- **Hybrid ML**: O(n_features × n_players × n_positions) for training

### Scalability
- Current implementation: ~700 FPL players
- Can handle full dataset comfortably
- Monte Carlo most time-intensive (1000 simulations)
- Consider reducing simulations for faster results

---

## References

**Primary Source:**
Ramezani, D. (2025). "Data-Driven Team Selection in Fantasy Premier League Using Integer Programming and Predictive Modeling Approach." arXiv:2505.02170 [cs.CE]

**Additional Reading:**
- Ben-Tal, A., & Nemirovski, A. (2002). Robust optimization–methodology and applications.
- Hyndman, R. J., & Athanasopoulos, G. (2018). Forecasting: principles and practice.
- Hastie, T., Tibshirani, R., & Friedman, J. (2009). The Elements of Statistical Learning.

---

**Document Version:** 1.0  
**Last Updated:** 2025-01-18
