import streamlit as st
import os
import numpy as np
import pandas as pd

# Safety imports
try:
    import joblib
    JOB_OK = True
except ImportError as e:
    st.error(f"joblib failed: {e}")
    JOB_OK = False

try:
    import xgboost
    XGBOST_OK = True
except ImportError as e:
    XGBOST_OK = False

try:
    import sklearn
    SK_OK = True
except ImportError as e:
    SK_OK = False

st.set_page_config(page_title="HELOC", page_icon="🏦", layout="wide")

st.title("🏦 HELOC Decision Support System")
st.markdown("### Machine Learning-Based Application Screening")

# Show what's loaded
st.sidebar.markdown("### Dependencies")
st.sidebar.write(f"✅ joblib: {JOB_OK}")
st.sidebar.write(f"✅ xgboost: {XGBOST_OK}")
st.sidebar.write(f"✅ sklearn: {SK_OK}")

if not JOB_OK:
    st.error("⚠️ Required library missing")
    st.stop()

# Try to load model
try:
    if os.path.exists("heloc_model.joblib"):
        model = joblib.load("heloc_model.joblib")
        st.sidebar.success("✅ Model loaded")
    else:
        st.sidebar.warning("⚠️ Model file not found")
        model = None
except Exception as e:
    st.sidebar.error(f"Error loading model: {e}")
    model = None

# Demo mode
st.success("✅ Application loaded successfully!")
st.write("If you see this, the app is working correctly.")
