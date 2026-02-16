"""
HELOC Decision Support System - Streamlit Cloud Edition
Robust error handling for cloud deployment
"""

import streamlit as st
import os
import sys

# Configure page
st.set_page_config(
    page_title="HELOC Decision Support System", 
    page_icon="🏦",
    layout="wide"
)

# Initialize session state for status
if 'imports_ok' not in st.session_state:
    st.session_state.imports_ok = True
    st.session_state.model_loaded = False
    st.session_state.errors = []

# Try imports one by one
try:
    import numpy as np
except ImportError as e:
    st.session_state.imports_ok = False
    st.session_state.errors.append(f"numpy: {e}")
    np = None

try:
    import pandas as pd
except ImportError as e:
    st.session_state.imports_ok = False
    st.session_state.errors.append(f"pandas: {e}")
    pd = None

try:
    import joblib
except ImportError as e:
    st.session_state.imports_ok = False
    st.session_state.errors.append(f"joblib: {e}")
    joblib = None

try:
    import xgboost
except ImportError as e:
    st.session_state.errors.append(f"xgboost (optional): {e}")
    xgboost = None

try:
    import sklearn
except ImportError as e:
    st.session_state.errors.append(f"sklearn (optional): {e}")
    sklearn = None

# Header
st.title("🏦 HELOC Decision Support System")
st.markdown("### Machine Learning-Based Application Screening")

# Status sidebar
with st.sidebar:
    st.markdown("### 📊 System Status")
    
    if st.session_state.imports_ok:
        st.success("✅ Core imports OK")
    else:
        st.error("❌ Missing core imports")
    
    if st.session_state.errors:
        with st.expander("⚠️ Issues"):
            for err in st.session_state.errors:
                st.write(f"- {err}")

# Check if we can proceed
if not st.session_state.imports_ok:
    st.error("Cannot load required libraries. Please ensure numpy, pandas, and joblib are installed.")
    st.stop()

# Try to load model
@st.cache_resource
def load_model_safely():
    """Safely load model with comprehensive error handling."""
    artifacts = {
        'model': None,
        'features': None,
        'threshold': 0.5,
        'error': None
    }
    
    try:
        # Try loading model
        if os.path.exists("heloc_model.joblib") and joblib is not None:
            try:
                artifacts['model'] = joblib.load("heloc_model.joblib")
            except Exception as e:
                artifacts['error'] = f"Model load failed: {type(e).__name__}: {str(e)[:100]}"
        
        # Try loading features
        if os.path.exists("feature_cols.joblib") and joblib is not None:
            try:
                artifacts['features'] = joblib.load("feature_cols.joblib")
            except Exception as e:
                artifacts['error'] = f"Features load failed: {type(e).__name__}"
        
        # Try loading threshold
        if os.path.exists("heloc_threshold.joblib") and joblib is not None:
            try:
                threshold = joblib.load("heloc_threshold.joblib")
                artifacts['threshold'] = float(threshold)
            except:
                pass
    except Exception as e:
        artifacts['error'] = f"Unexpected error: {type(e).__name__}"
    
    return artifacts

# Load model
artifacts = load_model_safely()
model = artifacts['model']
features = artifacts['features']
threshold = artifacts['threshold']

# Show model status
with st.sidebar:
    st.markdown("### 🤖 Model Status")
    
    if model is not None:
        st.success("✅ Model Loaded")
        st.session_state.model_loaded = True
    else:
        st.info("ℹ️ Demo Mode")
        if artifacts.get('error'):
            st.caption(f"Error: {artifacts['error']}")

# Main content
if model is not None:
    st.info("✅ Using ML Model for predictions")
else:
    st.warning("⚠️ Using simplified demo calculations")

# Demo section
st.markdown("---")
st.header("📋 Demo Application")
st.write("This demonstrates the HELOC Decision Support System.")

# Simple demo inputs
col1, col2 = st.columns(2)
with col1:
    credit_score = st.slider("Credit Score", 0, 100, 70)
    inquiries = st.slider("Recent Inquiries (6M)", 0, 10, 1)

with col2:
    utilization = st.slider("Credit Utilization %", 0, 100, 25)
    delinquencies = st.selectbox("Recent Delinquencies", ["None", "30 days", "60+ days"])

# Simple prediction
st.markdown("---")
st.header("🎯 Decision")

# Demo scoring
score = credit_score / 100.0
score -= (inquiries * 0.05)
score -= (utilization / 100.0) * 0.3
if delinquencies == "None":
    score += 0.1
elif delinquencies == "30 days":
    score -= 0.15

# Ensure score is between 0 and 1
score = max(0, min(1, score))

decision = "✅ Escalate for Review" if score >= threshold else "❌ Auto-Reject"
st.metric("Decision", decision)
st.progress(score, text=f"Score: {score:.1%}")

# Footer
st.markdown("---")
st.caption("© 2026 HELOC Decision Support System | For demonstration purposes only")
