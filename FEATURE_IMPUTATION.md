# Feature Imputation Strategy

## Problem Fixed

**Error**: `feature_names mismatch` - Model trained on 23 features but application only provided 5-6

```
Expected: ['ExternalRiskEstimate', 'MSinceOldestTradeOpen', 'MSinceMostRecentTradeOpen', 
           'AverageMInFile', 'NumSatisfactoryTrades', ...]  (23 total)

Received: ['ExternalRiskEstimate', 'Credit_History_Years', 'MSinceMostRecentDelq', 
           'NetFractionRevolvingBurden', 'NumInqLast6M', 'MaxDelq2PublicRecLast12M']  (6 with 1 invalid)
```

## Solution

**Median Imputation**: Use historical median values for missing features

### How It Works

1. **Load Median Values** (`heloc_medians.joblib` - 23 features)
   ```python
   medians = joblib.load("heloc_medians.joblib")
   # Contains: ExternalRiskEstimate: 72.0, MSinceOldestTradeOpen: 186.0, ...
   ```

2. **Collect User Input** (5 key features only - user-friendly)
   - ExternalRiskEstimate
   - MSinceMostRecentDelq  
   - NetFractionRevolvingBurden
   - NumInqLast6M
   - MaxDelq2PublicRecLast12M

3. **Combine & Fill** (start with medians, override with user input)
   ```python
   full_inputs = medians.copy()          # Start with all 23 medians
   full_inputs.update(user_inputs)       # Override with 5 user values
   # Result: 23 complete features
   ```

4. **Predict with Complete Feature Set**
   ```python
   df = pd.DataFrame([full_inputs])
   df = df[feature_names]  # Ensure correct column order
   proba = model.predict_proba(df)  # ✅ Now has all 23 features
   ```

## Feature Details

### 23 Model Features

| # | Feature | Type | Role |
|---|---------|------|------|
| 1 | ExternalRiskEstimate | User Input | Credit risk score (0-100) |
| 2 | MSinceOldestTradeOpen | Median-filled | Months since oldest trade account opened |
| 3 | MSinceMostRecentTradeOpen | Median-filled | Months since most recent trade account opened |
| 4 | AverageMInFile | Median-filled | Average months account in credit file |
| 5 | NumSatisfactoryTrades | Median-filled | Number of satisfactory trades |
| 6 | NumTrades60Ever2DerogPubRec | Median-filled | Trades 60+ days past due or derogatory |
| 7 | NumTrades90Ever2DerogPubRec | Median-filled | Trades 90+ days past due or derogatory |
| 8 | PercentTradesNeverDelq | Median-filled | Percentage of trades never delinquent |
| 9 | MSinceMostRecentDelq | User Input | Months since most recent delinquency |
| 10 | MaxDelq2PublicRecLast12M | User Input | Worst delinquency in last 12 months |
| 11 | MaxDelqEver | Median-filled | Worst delinquency ever |
| 12 | NumTotalTrades | Median-filled | Total number of trades |
| 13 | NumTradesOpeninLast12M | Median-filled | Trades opened in last 12 months |
| 14 | PercentInstallTrades | Median-filled | Percentage of installment trades |
| 15 | MSinceMostRecentInqexcl7days | Median-filled | Months since most recent inquiry (excl 7 days) |
| 16 | NumInqLast6M | User Input | Number of inquiries in last 6 months |
| 17 | NumInqLast6Mexcl7days | Median-filled | Inquiries in last 6 months (excl 7 days) |
| 18 | NetFractionRevolvingBurden | User Input | Credit card utilization ratio (0-1) |
| 19 | NetFractionInstallBurden | Median-filled | Installment credit burden ratio |
| 20 | NumRevolvingTradesWBalance | Median-filled | Number of revolving trades with balance |
| 21 | NumInstallTradesWBalance | Median-filled | Number of installment trades with balance |
| 22 | NumBank2NatlTradesWHighUtilization | Median-filled | Bank/national trades with high utilization |
| 23 | PercentTradesWBalance | Median-filled | Percentage of trades with balance |

### Median Values Used

```
ExternalRiskEstimate: 72.0
MSinceOldestTradeOpen: 186.0
MSinceMostRecentTradeOpen: 6.0
AverageMInFile: 76.0
NumSatisfactoryTrades: 20.0
NumTrades60Ever2DerogPubRec: 0.0
NumTrades90Ever2DerogPubRec: 0.0
PercentTradesNeverDelq: 97.0
MSinceMostRecentDelq: 15.0
MaxDelq2PublicRecLast12M: 6.0
MaxDelqEver: 6.0
NumTotalTrades: 21.0
NumTradesOpeninLast12M: 1.0
PercentInstallTrades: 33.0
MSinceMostRecentInqexcl7days: 0.0
NumInqLast6M: 1.0
NumInqLast6Mexcl7days: 1.0
NetFractionRevolvingBurden: 30.0 (but user input overrides)
NetFractionInstallBurden: 74.0
NumRevolvingTradesWBalance: 3.0
NumInstallTradesWBalance: 2.0
NumBank2NatlTradesWHighUtilization: 1.0
PercentTradesWBalance: 67.0
```

## Why This Approach Works

### ✅ Advantages

1. **User-Friendly**: Ask for only 5 easy-to-understand features
2. **Model-Compatible**: Provides all 23 features model expects
3. **Statistically Sound**: Median is a good imputation strategy for missing values
4. **Interpretable**: Users know which inputs affect their score
5. **Consistent**: Uses same feature values across all predictions
6. **Fallback**: If model unavailable, app still works with demo logic

### ⚠️ Assumptions

- Applicant demographics similar to historical data
- Trade history follows historical patterns (if not provided)
- Inquiry behavior follows historical patterns (if not provided)
- Delinquency behavior follows historical patterns (if not provided)

## Impact on Predictions

### Example: Two Applicants with Same 5 Inputs

Both have:
- ExternalRiskEstimate: 75
- MSinceMostRecentDelq: 24
- NetFractionRevolvingBurden: 0.25
- NumInqLast6M: 1
- MaxDelq2PublicRecLast12M: 6

**Same prediction result** because remaining 18 features filled with identical medians.

To get different predictions, user must provide one of the other 5 key features:
- Number of total trades
- Percentage of trades never delinquent
- Months since oldest trade opened
- Utilization on installment credit
- Other credit history details

## Imputation Limitations

**Features that cannot be overridden by user:**

The application currently only allows user input for 5 features. Other important factors use their historical medians:

- Trade history (age, count, types)
- Delinquency patterns (except recency)
- Inquiry quantity (6M period)
- Installment credit burden
- Account balance distribution

**Recommendation**: For comprehensive risk assessment, consider collecting additional user inputs for:
- NumTotalTrades (total number of credit accounts)
- PercentTradesNeverDelq (payment history percentage)  
- NumRevolvingTradesWBalance (active credit cards)
- MSinceOldestTradeOpen (credit age)

This would increase user input from 5 to 9 features and improve prediction personalization.

## Testing

```bash
# Test the imputation logic
python3 << 'EOF'
import joblib
import pandas as pd

features = joblib.load("feature_cols.joblib")
medians = joblib.load("heloc_medians.joblib")
model = joblib.load("heloc_model.joblib")

# 5 user inputs
inputs = {
    'ExternalRiskEstimate': 75,
    'MSinceMostRecentDelq': 24,
    'NetFractionRevolvingBurden': 0.25,
    'NumInqLast6M': 1,
    'MaxDelq2PublicRecLast12M': 6
}

# Imputation
full_inputs = medians.copy()
full_inputs.update(inputs)

# Predict
df = pd.DataFrame([full_inputs])[features]
proba = model.predict_proba(df)
print(f"Probability Good: {proba[0,1]:.3f}")
print(f"Probability Bad:  {proba[0,0]:.3f}")
EOF
```

Output:
```
Probability Good: 0.335
Probability Bad:  0.665
```

✅ Feature imputation working correctly!
