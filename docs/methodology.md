# Time-Series Forecasting & Inventory Optimization Methodology

## 1. Time-Series Formulation & Problem Framing

Demand forecasting in retail inventory management is framed as a **multi-step tabular time-series regression** problem across heterogeneous Store-Product pairs:

$$\hat{y}_{s, p, t+h} = f(\mathbf{x}_{s, p, t}, \mathbf{z}_{s, p, t+h})$$

Where:
- $s$: Store identifier
- $p$: Product SKU identifier
- $t$: Current origin timestamp (cutoff time)
- $h \in \{1, 2, \dots, H\}$: Forecast horizon in days (e.g., $H=14$ days)
- $\mathbf{x}_{s, p, t}$: Historical causal features available up to cutoff time $t$
- $\mathbf{z}_{s, p, t+h}$: Known future calendar/event features at step $t+h$ (day of week, month, scheduled promotions, holidays)

---

## 2. Preventing Data Leakage & Feature Engineering Rules

### Causal Feature Rules
1. **Lags**: Calculated strictly on $y_{s, p, t-k}$ for $k \ge 1$. For multi-day horizon direct/recursive models, lags strictly observe the prediction origin.
2. **Rolling Statistics**: Rolling mean and rolling standard deviation over windows $W \in \{7, 14, 28\}$ are calculated on shifted series ($y_{t-1}, y_{t-2}, \dots$).
3. **Calendar & Exogenous Attributes**:
   - `Day_of_Week` (0-6), `Is_Weekend` (0/1), `Month` (1-12), `Quarter` (1-4).
   - Cyclical encoding ($\sin/\cos$) for month and day of week.
   - Promotional status `Promotion` (0/1) and price discount percentage `Discount`.

---

## 3. Train, Validation & Test Splitting Strategy

Because retail demand is chronologically ordered with strong auto-correlation and seasonal trends, **random shuffling is strictly prohibited**.

```
[================= Training (70%) =================] [== Validation (15%) ==] [==== Test (15%) ====]
Origin -----------------------------------------> t_val_start ------------> t_test_start ------> T_end
```

- **Training Set (Earliest 70%)**: Model fitting and parameter estimation.
- **Validation Set (Next 15%)**: Hyperparameter tuning, feature selection, early stopping.
- **Test Set (Final 15%)**: Unseen out-of-time evaluation to report realistic generalized performance.
- **Walk-Forward Cross-Validation (Rolling Origin)**: Expanding window evaluation over 3 folds to test stability across different seasonal blocks.

---

## 4. Inventory Optimization Formulation

Forecasting demand is merely an intermediate step; the end objective is **operational decision-making**:

### A. Safety Stock ($SS$)
To absorb demand volatility during the supplier lead time ($L$) at a target service level $SL$ (e.g., 95% service level $\implies Z = 1.645$):

$$SS = Z \times \sigma_{\text{demand}} \times \sqrt{L}$$

Where $\sigma_{\text{demand}}$ is the standard deviation of daily forecast residual errors / historical demand, and $L$ is lead time in days.

### B. Reorder Point ($ROP$)
The inventory threshold triggering a replenishment purchase order:

$$ROP = (\bar{d} \times L) + SS$$

Where $\bar{d}$ is the average daily forecast demand over the lead time.

### C. Recommended Order Quantity ($ROQ$)
Given maximum warehouse capacity / target base-stock level $S_{\text{target}}$:

$$ROQ = \max(0, S_{\text{target}} - (\text{Current Stock} + \text{On Order})) \quad \text{when Current Stock} \le ROP$$

### D. Inventory Risk Matrix

| Risk State | Condition | Business Implication | Recommended Action |
| :--- | :--- | :--- | :--- |
| 🔴 **Stockout Risk** | $\text{Current Stock} < \text{Projected Lead Time Demand}$ | Imminent lost sales and lost customer goodwill | Immediate emergency PO reorder |
| 🟠 **Low Stock** | $\text{Projected Lead Time Demand} \le \text{Current Stock} \le ROP$ | Stock approaching safety buffer | Trigger standard replenishment PO |
| 🟢 **Healthy** | $ROP < \text{Current Stock} \le \text{Target Stock}$ | Optimal operating inventory | Maintain current schedule |
| 🔵 **Overstock Risk** | $\text{Current Stock} > \text{Target Stock} \times 1.5$ | Excess holding costs, cash lockup, shrinkage | Pause reorders / promote SKU |
