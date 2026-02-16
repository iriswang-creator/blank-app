# 🏦 HELOC Decision Support System

**Production-Grade Screening Tool for Home Equity Line of Credit Applications**

A professional Streamlit application designed for financial institutions to provide transparent, consistent, and fair HELOC application screening. This tool supports human decision-makers with data-driven insights while maintaining compliance and governance standards.

---

## 🎯 Overview

### Purpose
This system serves as a **screening recommendation tool**, not an automated approval engine. It provides:
- Initial applicant screening
- Risk assessment explanations
- Improvement guidance
- Loan officer review capabilities

The system is built on a Gradient Boosting model with **AUC of 0.7897** trained to identify loan performance risk.

### Key Design Principle
**All decisions require human review.** The system weighs false negatives (missing good loans) at 10x the cost of false positives to minimize denying creditworthy applicants.

---

## 📋 Application Features

### Dual-Mode Interface

#### 🧑‍💼 **Applicant Mode** (Simple, Customer-Facing)
- 6 intuitive input fields:
  - Credit Risk Score (0-100)
  - Credit History Length
  - Months Since Last Payment Issue
  - Credit Utilization Percentage
  - Recent Inquiries (6-month)
  - Worst Recent Payment Status
- Simple binary output:
  - ✓ "Pass Pre-Screening" → Proceed to manual review
  - ℹ️ "Not Approved for Fast-Track" → Consider improvements
- 4 plain-language risk explanations
- 3 actionable improvement suggestions
- No raw variable names or technical jargon

#### 👔 **Loan Officer Review Mode** (Advanced, Professional)
- Full control over all 5 input factors
- Adjustable decision threshold (0.30 - 0.90)
- Detailed risk probability display
- Pre-computed threshold comparison
- Structured data analysis table
- Model status and performance metrics
- Separate "About This Model" information

### Intelligent Prediction

The system uses a **dual-engine approach**:

1. **Production Mode** (When model available)
   - Uses trained XGBoost classifier
   - Returns probability scores
   - Integrates with heloc_model.joblib

2. **Demo Mode** (Fallback)
   - Rule-based business logic
   - Weights factors appropriately
   - Ensures usability if model unavailable

---

## 🚀 Quick Start

### Streamlit Community Cloud

1. Visit https://share.streamlit.io
2. Click "New app"
3. Select Repository: `iriswang-creator/blank-app`
4. Select Branch: `main`
5. Select File: `streamlit_app.py`
6. Click Deploy!

App will be live in 2-3 minutes.

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run streamlit_app.py

# Opens at http://localhost:8501
```

---

## 📊 Technical Stack

### Dependencies
```
streamlit >= 1.28.0      # Web framework
pandas >= 2.0.0          # Data operations
numpy >= 1.24.0          # Numerical computing
scikit-learn >= 1.3.0    # Model utilities
joblib >= 1.3.0          # Model serialization
xgboost >= 2.0.0         # Gradient boosting
```

### Model Artifacts
- `heloc_model.joblib` - Trained XGBoost classifier
- `feature_cols.joblib` - Feature column names
- `heloc_threshold.joblib` - Default threshold (0.80)
- `heloc_medians.joblib` - Median values for imputation

---

## 🎯 How It Works

### Applicant View Workflow
1. User enters 6 input fields
2. System calculates probability of good loan performance
3. Decision: Pass (≥0.80) or Hold (<0.80)
4. Display 4 risk explanations + 3 improvement suggestions
5. Advance to next step (manual review or refinement)

### Loan Officer View Workflow
1. Officer loads applicant data
2. Adjusts decision threshold (0.30-0.90) as needed
3. Reviews detailed risk analysis
4. Views model statistics and factor contributions
5. Makes informed recommendation to approver

### Prediction Logic
- **Input**: 6 credit metrics
- **Processing**: XGBoost model (or demo rules if unavailable)
- **Output**: Probability of good loan (0-100%)
- **Decision**: Compare to threshold

---

## 🏛️ Governance & Compliance

### Key Features
✓ **Disclaimer** - Clear statement that this is recommendation only  
✓ **Model Transparency** - AUC, algorithm, limitations documented  
✓ **Human Override** - Loan officers can adjust threshold  
✓ **Audit Trail Ready** - Structured for decision logging  
✓ **Fair Lending** - Explanations non-discriminatory  

### Must Implement (Institution)
- [ ] Access controls / authentication
- [ ] Decision audit logging
- [ ] Model performance monitoring quarterly
- [ ] Fair lending testing (demographic parity checks)
- [ ] Compliance with Fair Lending Act, ECOA, etc.

---

## 📈 Performance Metrics

| Metric | Value |
|--------|-------|
| Algorithm | XGBoost (Gradient Boosting) |
| AUC-ROC | 0.7897 |
| False Negative Weight | 10x (cost matters more) |
| Default Threshold | 0.80 (conservative) |
| Target Variable | Good vs Bad Loan Performance |

---

## 🔧 Customization Guide

### Change Decision Threshold
```python
default_threshold = 0.85  # Change from 0.80 to 0.85
```

### Modify Explanations
Edit `generate_explanations()` function for custom risk messaging.

### Adjust Factor Weights (Demo Mode)
Edit `demo_predict()` to change multipliers on risk factors:
```python
score = 1.0 - (inputs['ExternalRiskEstimate'] / 100.0) * 0.4
# Change 0.4 to adjust credit score weight
```

### Update Model
Replace `heloc_model.joblib` with new trained model, adjust `heloc_threshold.joblib` as needed.

---

## ⚠️ Important Notes

### Not Automated Decision System
This tool **recommends** but does not approve or deny applications. All decisions must be made by qualified loan officers.

### Regulatory Compliance
- Deploy institution responsible for Fair Lending compliance
- Must validate against training data disparities
- Keep audit logs of all decisions
- Comply with GDPR, CCPA, Fair Lending Act, ECOA

### Limitations
- Model trained on historical data (may reflect past biases)
- No real-time economic factors included
- Single algorithm (ensemble could be more robust)
- Threshold (0.80) should be validated with your portfolio

---

## 📞 Troubleshooting

### Model Not Loading
- Check heloc_model.joblib exists in repo root
- Verify joblib installed: `pip install joblib`
- App falls back to demo mode if unavailable

### Threshold Not Adjustable
- Threshold slider only in "Loan Officer Review" mode
- Applicant mode uses fixed 0.80 threshold

### App Slow to Start
- Normal: 30 seconds first run (model caching)
- Fast: <1 second on subsequent runs
- Check internet connection for Streamlit Cloud

---

## 📚 File Reference

| File | Purpose |
|------|---------|
| streamlit_app.py | Main application (628 lines) |
| requirements.txt | Python package dependencies |
| heloc_model.joblib | Trained XGBoost model |
| feature_cols.joblib | Feature column names |
| heloc_threshold.joblib | Default decision threshold |
| heloc_medians.joblib | Median values for preprocessing |
| README.md | This documentation |

---

## 🎓 Model Details

### Input Variables (6 Factors)
1. **ExternalRiskEstimate** (0-100) - Credit score proxy, higher = lower risk
2. **Credit_History_Years** (0-80) - Length of credit history
3. **MSinceMostRecentDelq** (-7 to 120) - Months since last delinquency (-7 = never)
4. **NetFractionRevolvingBurden** (0-1) - Revolving credit utilization ratio
5. **NumInqLast6M** (0-20) - Number of credit inquiries in last 6 months
6. **MaxDelq2PublicRecLast12M** (0-7) - Worst delinquency status in last 12 months

### Output
- **Probability of Good Loan** (0-100%)
- **Decision Rule**: Good% ≥ Threshold → Pass, else Hold

---

## 🚀 Deployment Checklist

- [x] Code complete and tested
- [x] requirements.txt updated
- [x] Model artifacts included
- [x] README documented
- [x] Deployed to GitHub
- [ ] Deployed to Streamlit Cloud (do this!)
- [ ] Access controls configured
- [ ] Audit logging implemented
- [ ] Fair lending tests completed
- [ ] Regulatory review passed

---

**Last Updated**: February 2026  
**Version**: 1.0 Production  
**Framework**: Streamlit 1.28+  
**Model**: XGBoost (AUC 0.7897)  
**Status**: Ready for Deployment
