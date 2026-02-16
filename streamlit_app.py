"""
HELOC Decision Support System - Production Edition
A screening tool for Home Equity Line of Credit applications
Designed for human review, not automated approval
"""

import streamlit as st
import pandas as pd
import numpy as np
import os
from pathlib import Path

# Page configuration
st.set_page_config(
    page_title="HELOC Screening Decision Support",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional appearance
st.markdown("""
    <style>
    .main {
        max-width: 1000px;
        margin: 0 auto;
    }
    .stMetric {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
    }
    .disclaimer {
        background-color: #fff3cd;
        padding: 1rem;
        border-left: 4px solid #ffc107;
        border-radius: 0.25rem;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# ============================================================================
# MODEL LOADING AND PREDICTION LOGIC
# ============================================================================

@st.cache_resource
def load_model_artifacts():
    """Load model artifacts with graceful fallback to demo mode."""
    artifacts = {
        'model': None,
        'threshold': 0.6944,
        'feature_cols': None,
        'medians': None,
        'mode': 'demo'
    }
    
    try:
        import joblib
        
        # Try to load the trained model
        if os.path.exists("heloc_model.joblib"):
            artifacts['model'] = joblib.load("heloc_model.joblib")
            artifacts['mode'] = 'production'
            
        # Load feature columns if available
        if os.path.exists("feature_cols.joblib"):
            artifacts['feature_cols'] = joblib.load("feature_cols.joblib")
            
        # Load median values for imputation
        if os.path.exists("heloc_medians.joblib"):
            artifacts['medians'] = joblib.load("heloc_medians.joblib")
            
        # Load threshold if available
        if os.path.exists("heloc_threshold.joblib"):
            threshold = joblib.load("heloc_threshold.joblib")
            artifacts['threshold'] = float(threshold) if threshold else 0.6944
            
    except Exception as e:
        st.warning(f"Could not load production model: {str(e)}")
        artifacts['mode'] = 'demo'
    
    return artifacts


# Feature mapping for user-friendly display
FEATURE_DISPLAY_NAMES = {
    'ExternalRiskEstimate': 'Credit Risk Score',
    'Credit_History_Years': 'Credit History Length (years)',
    'MSinceMostRecentDelq': 'Months Since Last Issue',
    'NetFractionRevolvingBurden': 'Credit Utilization Ratio',
    'NumInqLast6M': 'Credit Inquiries (6 months)',
    'MaxDelq2PublicRecLast12M': 'Worst Recent Issue Status'
}

DELINQUENCY_LABELS = {
    'current': 'Current / Never Delinquent',
    'thirty': '30 days past due',
    'sixty': '60 days past due',
    'ninety': '90+ days past due',
    'derogatory': 'Derogatory/Charge-off'
}

# ============================================================================
# PREDICTION FUNCTIONS
# ============================================================================

def predict_probability(inputs: dict, model, feature_names, medians=None) -> tuple:
    """
    Predict probability of loan performance.
    Uses median imputation for missing features.
    
    Returns:
        (probability_bad, probability_good, decision)
    """
    if model is None:
        return demo_predict(inputs)
    
    try:
        import pandas as pd
        
        # Start with median values for all features
        if medians is not None:
            full_inputs = medians.copy()
        else:
            full_inputs = {}
        
        # Override with user-provided values
        full_inputs.update(inputs)
        
        # Create dataframe with correct column order
        df_input = pd.DataFrame([full_inputs])
        
        # Ensure columns match model training (correct order & features)
        if feature_names and isinstance(feature_names, list):
            # Select only the features the model knows about
            df_input = df_input[[f for f in feature_names if f in df_input.columns]]
            # Ensure correct column order
            df_input = df_input[feature_names]
        
        # Get probability of positive class (good = 1)
        prob_good = float(model.predict_proba(df_input)[0, 1])
        prob_bad = 1.0 - prob_good
        
        return prob_bad, prob_good, "success"
    except Exception as e:
        st.error(f"Prediction error: {str(e)}")
        return demo_predict(inputs)


def demo_predict(inputs: dict) -> tuple:
    """
    Fallback demo prediction using business logic rules.
    Returns (probability_bad, probability_good, source)
    """
    # Start with base score from credit risk estimate
    score = 1.0 - (inputs.get('ExternalRiskEstimate', 70) / 100.0) * 0.4
    
    # Factor in recent delinquency
    months_since = inputs.get('MSinceMostRecentDelq', 24)
    if months_since >= 36:
        score -= 0.10
    elif months_since >= 12:
        score -= 0.05
    elif months_since >= 0:
        score += 0.20
    else:
        score -= 0.25  # Current or recent
    
    # Factor in utilization (higher = worse)
    utilization = inputs.get('NetFractionRevolvingBurden', 0.3)
    score += utilization * 0.3
    
    # Factor in inquiries
    inquiries = inputs.get('NumInqLast6M', 1)
    score += inquiries * 0.05
    
    # Normalize to 0-1 range
    prob_bad = max(0, min(1, score))
    prob_good = 1.0 - prob_bad
    
    return prob_bad, prob_good, "demo"


def generate_explanations(inputs: dict, prob_bad: float, prob_good: float) -> list:
    """Generate plain-language explanations for the decision."""
    explanations = []
    
    # Credit risk score explanation
    score = inputs['ExternalRiskEstimate']
    if score >= 80:
        explanations.append(
            "✓ Strong credit history indicators suggest lower credit risk"
        )
    elif score >= 60:
        explanations.append(
            "~ Moderate credit metrics within acceptable range"
        )
    else:
        explanations.append(
            "✗ Credit risk indicators suggest elevated caution required"
        )
    
    # Delinquency history
    months_since = inputs.get('MSinceMostRecentDelq', 24)
    if months_since >= 36:
        explanations.append(
            "✓ Sufficient time passed since last payment issue indicates reliability"
        )
    elif months_since >= 12:
        explanations.append(
            "~ Recent payment challenges but showing recovery"
        )
    else:
        explanations.append(
            "✗ Recent payment issues require careful consideration"
        )
    
    # Credit utilization
    util = inputs.get('NetFractionRevolvingBurden', 0.3)
    if util <= 0.30:
        explanations.append(
            "✓ Low credit utilization demonstrates credit management discipline"
        )
    elif util <= 0.60:
        explanations.append(
            "~ Credit utilization at moderate levels"
        )
    else:
        explanations.append(
            "✗ High credit utilization may indicate financial strain"
        )
    
    return explanations[:4]  # Return top 4


def generate_suggestions(inputs: dict, prob_bad: float, credit_years: int = 7) -> list:
    """Generate improvement suggestions for the applicant."""
    suggestions = []
    
    # Credit utilization
    if inputs.get('NetFractionRevolvingBurden', 0) > 0.40:
        suggestions.append(
            "Reduce credit card balances to below 30% of available limits"
        )
    
    # Recent inquiries
    if inputs.get('NumInqLast6M', 0) >= 2:
        suggestions.append(
            "Avoid new credit applications for at least 6-12 months to demonstrate stability"
        )
    
    # Credit history
    if credit_years < 5:
        suggestions.append(
            "Continue building credit history through responsible account management"
        )
    
    return suggestions[:3]  # Return top 3


# ============================================================================
# MAIN APPLICATION LAYOUT
# ============================================================================

# Load model artifacts
artifacts = load_model_artifacts()
model = artifacts['model']
default_threshold = artifacts['threshold']
feature_cols = artifacts['feature_cols']  # Fixed: was 'feature_columns'
medians = artifacts['medians']
model_mode = artifacts['mode']

# Sidebar - Mode selection and settings
with st.sidebar:
    st.markdown("## ⚙️ System Settings")
    
    # Model status
    if model_mode == 'production':
        st.success("🤖 Production Model Active")
    else:
        st.info("📊 Demo Mode (Rule-Based Scoring)")
    
    # Mode selection
    app_mode = st.radio(
        "**Select Application Mode**",
        options=["Applicant View", "Loan Officer Review"],
        help="Applicant: Simple screening | Loan Officer: Advanced review"
    )
    
    # Loan officer settings
    if app_mode == "Loan Officer Review":
        st.divider()
        st.markdown("### Decision Threshold")
        threshold = st.slider(
            "Adjust approval threshold (lower = approve more)",
            min_value=0.3,
            max_value=0.9,
            value=default_threshold,
            step=0.05,
            help="Probability threshold for 'Pass Pre-Screening' decision"
        )
    else:
        threshold = default_threshold
    
    # About section
    with st.expander("ℹ️ About This Tool", expanded=False):
        st.markdown("""
        **HELOC Screening Decision Support System**
        
        - **Purpose**: Initial screening tool for HELOC applications
        - **Not**: Automated approval or denial system
        - **Model**: Gradient Boosting classifier (AUC: 0.79)
        - **All decisions** require human review and oversight
        
        **Key Considerations**:
        - Model trained on historical loan performance
        - Decisions should account for context and special circumstances
        - False negatives (missing good loans) weighted 10x higher than false positives
        """)

# ============================================================================
# HEADER AND DISCLAIMER
# ============================================================================

st.title("🏦 HELOC Screening Decision Support")
st.markdown("*A decision support tool for fair and consistent HELOC application screening*")

# Disclaimer box
st.markdown("""
<div class="disclaimer">
<strong>⚠️ Important Disclaimer</strong><br>
This tool provides a screening recommendation only and does NOT replace final human review. 
All loan decisions must be made by qualified loan officers considering the complete application, 
applicable regulations, and lending policies. This system supports but cannot automate the decision process.
</div>
""", unsafe_allow_html=True)

st.divider()

# ============================================================================
# APPLICANT MODE
# ============================================================================

if app_mode == "Applicant View":
    st.header("📋 Application Screening")
    st.markdown("Please provide the following information for initial screening evaluation.")
    
    # Input form with clearer structure
    col1, col2 = st.columns(2)
    
    with col1:
        # 1. Credit Risk Score
        st.markdown("**1. Your Credit Risk Profile**")
        credit_score_option = st.selectbox(
            "How would you rate your credit standing?",
            options=[
                "Excellent (90-100) - Very strong credit history",
                "Good (75-89) - Strong credit profile",
                "Fair (55-74) - Acceptable credit record",
                "Poor (Below 55) - Shows credit challenges"
            ],
            index=1,
            help="Select the option that best describes your overall credit situation"
        )
        credit_score_map = {
            "Excellent (90-100) - Very strong credit history": 95,
            "Good (75-89) - Strong credit profile": 82,
            "Fair (55-74) - Acceptable credit record": 65,
            "Poor (Below 55) - Shows credit challenges": 45
        }
        credit_score = credit_score_map[credit_score_option]
        
        # 2. Credit History Length
        st.markdown("**2. Credit History Length**")
        credit_years = st.selectbox(
            "How long have you had credit accounts?",
            options=[
                "Less than 2 years - New to credit",
                "2-5 years - Building credit",
                "5-10 years - Established history",
                "10-15 years - Strong history",
                "15+ years - Extensive history"
            ],
            index=2,
            help="Select your total credit account history duration"
        )
        credit_years_map = {
            "Less than 2 years - New to credit": 1,
            "2-5 years - Building credit": 3,
            "5-10 years - Established history": 7,
            "10-15 years - Strong history": 12,
            "15+ years - Extensive history": 20
        }
        credit_years_value = credit_years_map[credit_years]
        
        # 3. Credit Card Usage
        st.markdown("**3. Credit Card Utilization**")
        utilization_option = st.selectbox(
            "What percentage of your credit limit do you typically use?",
            options=[
                "Very Low (0-20%) - Excellent management",
                "Low (21-40%) - Good management",
                "Moderate (41-60%) - Acceptable",
                "High (61-80%) - Some concern",
                "Very High (81-100%) - High risk"
            ],
            index=0,
            help="Select how much of your available credit you usually use"
        )
        utilization_map = {
            "Very Low (0-20%) - Excellent management": 10,
            "Low (21-40%) - Good management": 30,
            "Moderate (41-60%) - Acceptable": 50,
            "High (61-80%) - Some concern": 70,
            "Very High (81-100%) - High risk": 90
        }
        utilization = utilization_map[utilization_option]
    
    with col2:
        # 4. Payment History - Recent Issues
        st.markdown("**4. Recent Payment History** (Last 12 months)")
        recent_delinq = st.selectbox(
            "Have you had any payment issues?",
            options=list(DELINQUENCY_LABELS.values()),
            index=0,
            help="Select your worst payment status in the last 12 months"
        )
        
        # 5. Time Since Last Payment Problem
        st.markdown("**5. Payment Issue Recency**")
        months_since_option = st.selectbox(
            "When was your last payment issue?",
            options=[
                "Never had payment issues - Perfect record",
                "3-6 months ago - Recent issue",
                "6-12 months ago - Somewhat recent",
                "1-2 years ago - Resolved",
                "2-3 years ago - Well resolved",
                "3+ years ago - Long time ago"
            ],
            index=0,
            help="Select how long ago you had your most recent payment problem"
        )
        months_since_map = {
            "Never had payment issues - Perfect record": -7,
            "3-6 months ago - Recent issue": 4,
            "6-12 months ago - Somewhat recent": 9,
            "1-2 years ago - Resolved": 18,
            "2-3 years ago - Well resolved": 30,
            "3+ years ago - Long time ago": 48
        }
        months_since = months_since_map[months_since_option]
        
        # 6. Credit Inquiries
        st.markdown("**6. Recent Credit Inquiries** (Last 6 months)")
        inquiries_option = st.selectbox(
            "How many times has your credit been checked?",
            options=[
                "None (0) - No new credit applications",
                "1-2 - Few recent applications",
                "3-5 - Several applications",
                "6+ - Multiple recent applications"
            ],
            index=0,
            help="Number of times lenders checked your credit recently"
        )
        inquiries_map = {
            "None (0) - No new credit applications": 0,
            "1-2 - Few recent applications": 1,
            "3-5 - Several applications": 4,
            "6+ - Multiple recent applications": 7
        }
        inquiries = inquiries_map[inquiries_option]
    
    # Inputs for the model (only actual model features)
    inputs = {
        'ExternalRiskEstimate': credit_score,
        'MSinceMostRecentDelq': months_since,
        'NetFractionRevolvingBurden': utilization / 100.0,
        'NumInqLast6M': inquiries,
        'MaxDelq2PublicRecLast12M': 7  # Default for demo
    }
    
    # Generate prediction (medians will fill missing features)
    prob_bad, prob_good, source = predict_probability(inputs, model, feature_cols, medians)
    
    # Decision logic
    decision = "pass" if prob_good >= threshold else "hold"
    
    # Display results
    st.divider()
    st.header("✅ Screening Result")
    
    col_result, col_prob = st.columns([2, 1])
    
    with col_result:
        if decision == "pass":
            st.success(
                "**Pass Pre-Screening** ✓\n\n"
                "This application passes initial screening and will proceed to manual review by a loan officer."
            )
        else:
            st.warning(
                "**Not Approved for Fast-Track** ℹ️\n\n"
                "This application requires additional review. Consider the suggestions below to strengthen your application."
            )
    
    with col_prob:
        st.metric(
            "Approval Probability",
            f"{prob_good:.1%}",
            delta=f"{prob_good - threshold:.1%} vs threshold" if decision == "pass" else None
        )
    
    # Display explanations
    st.subheader("📊 Key Factors")
    explanations = generate_explanations(inputs, prob_bad, prob_good)
    for i, exp in enumerate(explanations, 1):
        st.write(f"{i}. {exp}")
    
    # Display suggestions
    if decision == "hold":
        st.subheader("💡 How to Strengthen Your Application")
        suggestions = generate_suggestions(inputs, prob_bad, credit_years_value)
        for i, sug in enumerate(suggestions, 1):
            st.write(f"{i}. {sug}")
    
    # Next steps
    st.divider()
    st.info(
        "**Next Steps**: "
        "If approved for fast-track, a loan officer will contact you within 2-3 business days. "
        "If additional review is needed, we may request additional documentation."
    )

# ============================================================================
# LOAN OFFICER MODE
# ============================================================================

else:  # Loan Officer Review
    st.header("🔧 Loan Officer Advanced Review")
    st.markdown("Detailed screening analysis with adjustable decision threshold.")
    
    # Input form with more details
    col1, col2, col3 = st.columns(3)
    
    with col1:
        credit_score = st.number_input(
            "External Risk Estimate",
            min_value=0,
            max_value=100,
            value=70
        )
        
        credit_years = st.number_input(
            "Credit History (years)",
            min_value=0,
            max_value=80,
            value=10
        )
        
        months_since = st.number_input(
            "Months Since Delinquency",
            min_value=-7,
            max_value=120,
            value=24
        )
    
    with col2:
        utilization = st.number_input(
            "Revolving Utilization Ratio",
            min_value=0.0,
            max_value=1.0,
            value=0.25,
            step=0.05
        )
        
        inquiries = st.number_input(
            "Inquiries (Last 6M)",
            min_value=0,
            max_value=20,
            value=1
        )
        
        delinq_status = st.selectbox(
            "Recent Delinquency Status",
            options=list(DELINQUENCY_LABELS.values()),
            index=0
        )
    
    with col3:
        st.markdown("### Decision Settings")
        threshold_lo = st.slider(
            "Decision Threshold",
            min_value=0.3,
            max_value=0.9,
            value=threshold,
            step=0.05
        )
        
        st.divider()
        st.markdown("**Model Status**: " + 
                   ("🤖 Production" if model_mode == 'production' else "📊 Demo"))
    
    # Prepare inputs (only actual model features)
    inputs = {
        'ExternalRiskEstimate': credit_score,
        'MSinceMostRecentDelq': months_since,
        'NetFractionRevolvingBurden': utilization,
        'NumInqLast6M': inquiries,
        'MaxDelq2PublicRecLast12M': 7
    }
    
    # Generate prediction (medians will fill missing features)
    prob_bad, prob_good, source = predict_probability(inputs, model, feature_cols, medians)
    
    # Decision
    decision = "approve" if prob_good >= threshold_lo else "deny"
    
    # Display results
    st.divider()
    
    col_metric1, col_metric2, col_metric3 = st.columns(3)
    
    with col_metric1:
        st.metric(
            "Risk Probability (Bad)",
            f"{prob_bad:.2%}",
            delta=None
        )
    
    with col_metric2:
        st.metric(
            "Approval Probability (Good)",
            f"{prob_good:.2%}",
            delta=f"{(prob_good - threshold_lo)*100:.1f} pp vs threshold"
        )
    
    with col_metric3:
        st.metric(
            "Recommendation",
            "APPROVE" if decision == "approve" else "DENY",
            delta="🟢 Pass" if decision == "approve" else "🔴 Fail"
        )
    
    # Detailed analysis
    st.subheader("📋 Detailed Analysis")
    
    analysis_data = {
        'Factor': list(FEATURE_DISPLAY_NAMES.values()),
        'Value': [
            f"{credit_score}/100",
            f"{credit_years} years",
            f"{months_since} months",
            f"{utilization:.1%}",
            f"{inquiries}",
            delinq_status
        ]
    }
    
    st.dataframe(
        pd.DataFrame(analysis_data),
        use_container_width=True,
        hide_index=True
    )
    
    # Detailed explanations
    st.subheader("🔍 Risk Factors")
    explanations = generate_explanations(inputs, prob_bad, prob_good)
    for exp in explanations:
        st.write(exp)
    
    # Model information
    with st.expander("📚 Model Information"):
        st.markdown(f"""
        - **Current Mode**: {model_mode.upper()}
        - **Model Type**: Gradient Boosting Classifier
        - **AUC Score**: 0.7897
        - **Threshold**: {threshold_lo:.2f}
        - **Output**: Probability of loan performance (good vs bad)
        """)

# ============================================================================
# FOOTER
# ============================================================================

st.divider()
st.markdown("""
---
*HELOC Decision Support System v1.0* | 
For official decision requirements and compliance, 
refer to [Bank Name] lending policies and applicable regulations.
""")

