"""
Minimal HELOC Application for Streamlit Cloud
This is a simpler version to use if the main app encounters deployment issues.
"""

import streamlit as st
import os
import numpy as np
import pandas as pd
import joblib

st.set_page_config(
    page_title="HELOC Decision Support System",
    page_icon="🏦",
    layout="wide"
)

st.title("🏦 HELOC Decision Support System")
st.markdown("### Machine Learning-Based Application Screening")

# Load model silently
@st.cache_resource
def load_model():
    model = None
    feature_cols = None
    threshold = 0.5
    
    try:
        if os.path.exists("heloc_model.joblib"):
            model = joblib.load("heloc_model.joblib")
        if os.path.exists("feature_cols.joblib"):
            feature_cols = joblib.load("feature_cols.joblib")
        if os.path.exists("heloc_threshold.joblib"):
            threshold = joblib.load("heloc_threshold.joblib")
    except:
        pass
    
    return model, feature_cols, threshold

model, feature_cols, threshold = load_model()

# Sidebar
st.sidebar.markdown("### Status")
if model:
    st.sidebar.success("✅ Model Loaded")
else:
    st.sidebar.info("ℹ️ Demo Mode")

# Main content
st.write("""
This is a simplified version of the HELOC Decision Support System.
""")

# Demo feature values
demo_features = {
    'ExternalRiskEstimate': 70,
    'NumInqLast6M': 1,
    'NetFractionRevolvingBurden': 0.25,
    'MaxDelq2PublicRecLast12M': 7,
    'MSinceMostRecentDelq': -7
}

st.subheader("Sample Input")
col1, col2 = st.columns(2)
with col1:
    for key, val in list(demo_features.items())[:3]:
        st.write(f"**{key}**: {val}")
with col2:
    for key, val in list(demo_features.items())[3:]:
        st.write(f"**{key}**: {val}")

st.success("✅ Application is running!")
