import streamlit as st

st.title("🎈 My new Streamlit app")
st.write(
    "Let's start building! For help and inspiration, head over to [docs.streamlit.io](https://docs.streamlit.io/)."
)
import os
import pickle
import numpy as np
import pandas as pd
import streamlit as st

st.set_page_config(page_title="HELOC Screening Prototype (Credit Risk)", layout="wide")

MODEL_PATH = "model.pkl"

# =============================
# Feature list (align to training order!)
# =============================
FEATURES = [
    "ExternalRiskEstimate",
    "MSinceOldestTradeOpen",
    "MSinceMostRecentTradeOpen",
    "AverageMInFile",
    "NumSatisfactoryTrades",
    "NumTrades60Ever2DerogPubRec",
    "NumTrades90Ever2DerogPubRec",
    "PercentTradesNeverDelq",
    "MSinceMostRecentDelq",
    "MaxDelq2PublicRecLast12M",
    "MaxDelqEver",
    "NumTotalTrades",
    "NumTradesOpeninLast12M",
    "PercentInstallTrades",
    "MSinceMostRecentInqexcl7days",
    "NumInqLast6M",
    "NumInqLast6Mexcl7days",
    "NetFractionRevolvingBurden",
    "NetFractionInstallBurden",
    "NumRevolvingTradesWBalance",
    "NumInstallTradesWBalance",
    "NumBank2NatlTradesWHighUtilization",
    "PercentTradesWBalance",
]

# =============================
# Helpers
# =============================
@st.cache_resource
def load_model(path: str):
    if not os.path.exists(path):
        return None
    with open(path, "rb") as f:
        return pickle.load(f)

def make_input_df(user_inputs: dict) -> pd.DataFrame:
    row = {k: user_inputs.get(k) for k in FEATURES}
    return pd.DataFrame([row], columns=FEATURES)

def safe_predict_proba_bad(model, X: pd.DataFrame) -> float:
    """
    Return P(bad=1). Assumes sklearn-like classifier with predict_proba.
    If your positive class is not at index 1, adjust here.
    """
    proba = model.predict_proba(X)
    return float(proba[0, 1])

def sigmoid(z: float) -> float:
    return float(1 / (1 + np.exp(-z)))

# =============================
# UI
# =============================
st.title("HELOC Screening Decision Support (Prototype)")
st.caption("Outputs a screening recommendation based on estimated probability of **bad = 1** (higher = riskier).")

model = load_model(MODEL_PATH)

# Delinquency code mappings (from your provided tables)
MAXDELQ12M_OPTIONS = [
    (7, "Current and never delinquent (Best)"),
    (4, "30 days delinquent"),
    (3, "60 days delinquent"),
    (2, "90 days delinquent"),
    (1, "120+ days delinquent"),
    (0, "Derogatory comment (Worst)"),
    (5, "Unknown delinquency (5)"),
    (6, "Unknown delinquency (6)"),
    (8, "All other (8)"),
    (9, "All other (9)"),
]

MAXDELQEVER_OPTIONS = [
    (8, "Current and never delinquent (Best)"),
    (6, "30 days delinquent"),
    (5, "60 days delinquent"),
    (4, "90 days delinquent"),
    (3, "120+ days delinquent"),
    (2, "Derogatory comment"),
    (7, "Unknown delinquency"),
    (9, "All other"),
    (1, "No such value (rare)"),
]

col_left, col_right = st.columns([1, 1])

with col_left:
    st.subheader("Applicant Inputs")

    # NOTE: Ranges below are reasonable defaults for demo.
    # Adjust after you check your dataset distributions (Task 2).
    ExternalRiskEstimate = st.slider("ExternalRiskEstimate (higher = lower risk)", 0, 100, 70, 1)

    MSinceOldestTradeOpen = st.number_input("Months Since Oldest Trade Open", min_value=0, value=120, step=1)
    MSinceMostRecentTradeOpen = st.number_input("Months Since Most Recent Trade Open", min_value=0, value=12, step=1)
    AverageMInFile = st.number_input("Average Months in File", min_value=0, value=60, step=1)

    NumSatisfactoryTrades = st.number_input("Num Satisfactory Trades", min_value=0, value=10, step=1)
    NumTotalTrades = st.number_input("Num Total Trades", min_value=0, value=15, step=1)
    NumTradesOpeninLast12M = st.number_input("Trades Opened in Last 12 Months", min_value=0, value=1, step=1)

    PercentTradesNeverDelq = st.slider("Percent Trades Never Delinquent", 0.0, 100.0, 95.0, 0.5)
    MSinceMostRecentDelq = st.number_input("Months Since Most Recent Delinquency", min_value=0, value=36, step=1)

    # Encoded delinquency fields
    MaxDelq2PublicRecLast12M = st.selectbox(
        "MaxDelq2PublicRecLast12M (Worst status in last 12M)",
        options=MAXDELQ12M_OPTIONS,
        format_func=lambda x: f"{x[0]} — {x[1]}",
        index=0,
    )[0]

    MaxDelqEver = st.selectbox(
        "MaxDelqEver (Worst status ever)",
        options=MAXDELQEVER_OPTIONS,
        format_func=lambda x: f"{x[0]} — {x[1]}",
        index=0,
    )[0]

    NumTrades60Ever2DerogPubRec = st.number_input("Num Trades 60+ Ever (Derog/Public Record)", min_value=0, value=0, step=1)
    NumTrades90Ever2DerogPubRec = st.number_input("Num Trades 90+ Ever (Derog/Public Record)", min_value=0, value=0, step=1)

    # Inquiries
    MSinceMostRecentInqexcl7days = st.number_input("Months Since Most Recent Inquiry (excl 7 days)", min_value=0, value=3, step=1)
    NumInqLast6M = st.number_input("Num Inquiries Last 6 Months", min_value=0, value=1, step=1)
    NumInqLast6Mexcl7days = st.number_input("Num Inquiries Last 6 Months (excl 7 days)", min_value=0, value=1, step=1)

    # Utilization / burden
    NetFractionRevolvingBurden = st.slider("Net Fraction Revolving Burden (higher = higher risk)", 0.0, 1.0, 0.25, 0.01)
    NetFractionInstallBurden = st.slider("Net Fraction Installment Burden (higher = higher risk)", 0.0, 1.0, 0.15, 0.01)

    NumRevolvingTradesWBalance = st.number_input("Num Revolving Trades with Balance", min_value=0, value=2, step=1)
    NumInstallTradesWBalance = st.number_input("Num Installment Trades with Balance", min_value=0, value=2, step=1)

    NumBank2NatlTradesWHighUtilization = st.number_input("Num Bank/Natl Trades with High Utilization", min_value=0, value=0, step=1)
    PercentInstallTrades = st.slider("Percent Installment Trades", 0.0, 100.0, 40.0, 0.5)
    PercentTradesWBalance = st.slider("Percent Trades with Balance", 0.0, 100.0, 60.0, 0.5)

    st.divider()
    deny_threshold = st.slider(
        "Deny Threshold (if P(bad=1) ≥ threshold → recommend Screen Out)",
        0.0, 1.0, 0.80, 0.01
    )

    user_inputs = {
        "ExternalRiskEstimate": ExternalRiskEstimate,
        "MSinceOldestTradeOpen": MSinceOldestTradeOpen,
        "MSinceMostRecentTradeOpen": MSinceMostRecentTradeOpen,
        "AverageMInFile": AverageMInFile,
        "NumSatisfactoryTrades": NumSatisfactoryTrades,
        "NumTrades60Ever2DerogPubRec": NumTrades60Ever2DerogPubRec,
        "NumTrades90Ever2DerogPubRec": NumTrades90Ever2DerogPubRec,
        "PercentTradesNeverDelq": PercentTradesNeverDelq,
        "MSinceMostRecentDelq": MSinceMostRecentDelq,
        "MaxDelq2PublicRecLast12M": MaxDelq2PublicRecLast12M,
        "MaxDelqEver": MaxDelqEver,
        "NumTotalTrades": NumTotalTrades,
        "NumTradesOpeninLast12M": NumTradesOpeninLast12M,
        "PercentInstallTrades": PercentInstallTrades,
        "MSinceMostRecentInqexcl7days": MSinceMostRecentInqexcl7days,
        "NumInqLast6M": NumInqLast6M,
        "NumInqLast6Mexcl7days": NumInqLast6Mexcl7days,
        "NetFractionRevolvingBurden": NetFractionRevolvingBurden,
        "NetFractionInstallBurden": NetFractionInstallBurden,
        "NumRevolvingTradesWBalance": NumRevolvingTradesWBalance,
        "NumInstallTradesWBalance": NumInstallTradesWBalance,
        "NumBank2NatlTradesWHighUtilization": NumBank2NatlTradesWHighUtilization,
        "PercentTradesWBalance": PercentTradesWBalance,
    }

    X = make_input_df(user_inputs)
    st.markdown("**Model Input (debug view)**")
    st.dataframe(X, use_container_width=True)

with col_right:
    st.subheader("Screening Output")

    if model is None:
        st.warning(
            "No trained model found (model.pkl). Running in DEMO mode.\n\n"
            "To connect your ML results: place your trained sklearn model at ./model.pkl "
            "and ensure FEATURES matches the training feature order."
        )

        # Simple demo risk score (NOT a real credit model)
        demo_score = (
            -0.03 * ExternalRiskEstimate
            + 2.2 * NetFractionRevolvingBurden
            + 1.4 * NetFractionInstallBurden
            + 0.12 * NumInqLast6M
            + 0.15 * NumBank2NatlTradesWHighUtilization
            - 0.01 * MSinceOldestTradeOpen
            - 0.008 * MSinceMostRecentDelq
            - 0.02 * PercentTradesNeverDelq
            + 0.18 * NumTrades90Ever2DerogPubRec
            + 0.10 * NumTrades60Ever2DerogPubRec
        )

        # Delinquency codes: smaller is generally worse → add risk when code is low
        if MaxDelq2PublicRecLast12M <= 2:
            demo_score += 1.2
        elif MaxDelq2PublicRecLast12M <= 4:
            demo_score += 0.6

        if MaxDelqEver <= 4:
            demo_score += 0.8
        elif MaxDelqEver <= 6:
            demo_score += 0.4

        prob_bad = sigmoid(demo_score)

    else:
        try:
            prob_bad = safe_predict_proba_bad(model, X)
        except Exception as e:
            st.error(f"Model loaded but prediction failed: {e}")
            st.stop()

    recommendation = "Screen Out (Deny)" if prob_bad >= deny_threshold else "Escalate for Manual Review"

    st.metric(label="Estimated Probability of Bad Outcome (bad = 1)", value=f"{prob_bad:.1%}")
    st.markdown(f"### Recommendation: **{recommendation}**")

    st.divider()
    st.subheader("Explanation (MVP)")

    # Lightweight rule-based narrative consistent with feature direction
    reasons = []
    if ExternalRiskEstimate < 50:
        reasons.append("Lower ExternalRiskEstimate suggests elevated baseline credit risk.")
    if NetFractionRevolvingBurden > 0.35:
        reasons.append("High revolving burden indicates higher utilization/financial strain.")
    if NumInqLast6M >= 4:
        reasons.append("Multiple recent inquiries may indicate increased credit-seeking behavior.")
    if MSinceMostRecentDelq < 12:
        reasons.append("Recent delinquency (few months since last delinquency) increases risk.")
    if MaxDelq2PublicRecLast12M in [0, 1, 2]:
        reasons.append("Severe delinquency status in the last 12 months materially increases risk.")
    if not reasons:
        reasons.append("Overall profile shows relatively low risk signals based on key indicators.")

    for r in reasons[:4]:
        st.write(f"- {r}")

    st.subheader("How to Improve (MVP)")
    tips = []
    if NetFractionRevolvingBurden > 0.35:
        tips.append("Reduce revolving balances to lower utilization ratios.")
    if NumInqLast6M >= 3:
        tips.append("Avoid new credit inquiries for 6–12 months if possible.")
    if MSinceMostRecentDelq < 12 or MaxDelq2PublicRecLast12M in [0, 1, 2, 3, 4]:
        tips.append("Maintain on-time payments to increase months since last delinquency.")
    if ExternalRiskEstimate < 50:
        tips.append("Focus on improving overall credit standing (e.g., reduce utilization, pay on time).")
    if not tips:
        tips = ["Maintain current financial profile and provide complete documentation for review."]
    for t in tips[:4]:
        st.write(f"- {t}")

st.divider()
st.caption(
    "Disclaimer: This tool provides a screening recommendation and does not replace final human review. "
    "All decisions remain subject to bank policy and regulatory requirements."
)
