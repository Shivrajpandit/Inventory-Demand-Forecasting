# Model Evaluation & Diagnostic Protocol

## 1. Evaluation Metrics

To rigorously assess forecasting accuracy without bias, the system tracks and computes four primary metrics on out-of-time test partitions:

### A. Mean Absolute Error (MAE)
Measures the average magnitude of absolute errors in units:
$$\text{MAE} = \frac{1}{N} \sum_{i=1}^{N} |y_i - \hat{y}_i|$$

### B. Root Mean Squared Error (RMSE)
Penalizes large outlier forecast errors heavily, crucial for preventing catastrophic stockouts:
$$\text{RMSE} = \sqrt{\frac{1}{N} \sum_{i=1}^{N} (y_i - \hat{y}_i)^2}$$

### C. Weighted Absolute Percentage Error (WAPE)
Standard percentage error metric robust to low-volume or zero-sales days (avoiding division-by-zero that breaks standard MAPE):
$$\text{WAPE} = \frac{\sum_{i=1}^N |y_i - \hat{y}_i|}{\sum_{i=1}^N y_i} \times 100\%$$

### D. Symmetric Mean Absolute Percentage Error (sMAPE)
Bound between 0% and 200%, providing balanced penalization for under-forecasting vs over-forecasting:
$$\text{sMAPE} = \frac{100\%}{N} \sum_{i=1}^N \frac{2 |y_i - \hat{y}_i|}{|y_i| + |\hat{y}_i|}$$

---

## 2. Model Tiering & Benchmark Hierarchy

Every experiment compares a strict progression of model complexities:

1. **Baseline 1: Naive Persistence (Last Known Sales)**:
   - $\hat{y}_{t+h} = y_{t}$ (or same day last week $y_{t+h-7}$).
2. **Baseline 2: 7-Day & 14-Day Simple Moving Average (SMA)**:
   - $\hat{y}_{t+h} = \frac{1}{7} \sum_{k=0}^6 y_{t-k}$.
3. **Statistical Model: SARIMAX / Exponential Smoothing**:
   - Captures univariate auto-regressive and seasonal components.
4. **Machine Learning Model: Regularized Ridge Regression**:
   - Linear baseline incorporating temporal, pricing, and lag features.
5. **Ensemble Trees: Random Forest Regressor**:
   - Non-linear relationships, robust against feature scaling.
6. **Gradient Boosted Trees: XGBoost & LightGBM**:
   - State-of-the-art tabular time-series forecast performance with custom objective functions.

---

## 3. Walk-Forward Validation Protocol

```
Fold 1: Train [Months 1-14] ---> Validate [Month 15]
Fold 2: Train [Months 1-16] ---> Validate [Month 17]
Fold 3: Train [Months 1-18] ---> Validate [Month 19]
Final:  Train [Months 1-20] ---> Holdout Test [Months 21-24]
```

- Each model is fitted on expanding training windows.
- Hyperparameters are tuned on validation splits.
- Model performance is reported on the holdout test set with real computed numbers.
