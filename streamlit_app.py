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

st.set_page_config(page_title="HELOC Application Pre-Screening", layout="centered")

# =========================
# (A) ML model placeholder
# =========================
MODEL_PATH = "model.pkl"

@st.cache_resource
def load_model(path: str):
    """Load trained model if available; otherwise return None."""
    if not os.path.exists(path):
        return None
    with open(path, "rb") as f:
        return pickle.load(f)

model = load_model(MODEL_PATH)

def sigmoid(z: float) -> float:
    return float(1 / (1 + np.exp(-z)))

def predict_prob_bad(inputs: dict) -> float:
    """
    Return P(bad = 1). Higher means riskier.

    ✅ CURRENT: rule-based demo (so prototype runs without ML)
    ✅ TODO: replace with real ML model:
        - build a DataFrame in training feature order
        - prob_bad = model.predict_proba(X)[0, 1]
    """
    if model is not None:
        # -----------------------------
        # TODO: Replace with your model
        # -----------------------------
        # Example skeleton:
        # X = pd.DataFrame([inputs])  # only works if columns match training exactly
        # prob_bad = float(model.predict_proba(X)[0, 1])
        # return prob_bad
        pass

    # ---- Demo risk score (NOT a real credit model) ----
    score = 0.0

    # ExternalRiskEstimate: higher is better -> reduces risk
    score += -0.04 * inputs["ExternalRiskEstimate"]

    # Utilization: higher is worse -> increases risk
    score += 2.0 * inputs["NetFractionRevolvingBurden"]

    # Recent inquiries: more is worse -> increases risk
    score += 0.18 * inputs["NumInqLast6M"]

    # Months since delinquency: longer is better -> reduces risk
    score += -0.01 * inputs["MSinceMostRecentDelq"]

    # Last 12M delinquency severity code: lower is worse
    md12 = inputs["MaxDelq2PublicRecLast12M"]
    if md12 in [0, 1, 2]:
        score += 1.2
    elif md12 in [3, 4]:
        score += 0.6

    # Credit history length (years): longer is better -> reduces risk
    score += -0.02 * inputs["CreditHistoryYears"]

    return sigmoid(score)

# =========================
# (B) Explanation generator
# =========================
def build_reasons(inputs: dict) -> tuple[list[str], list[str]]:
    """
    Return (reasons_for_result, improvement_tips) in plain language.
    """
    reasons = []
    tips = []

    # Convert utilization to %
    util_pct = int(round(inputs["NetFractionRevolvingBurden"] * 100))

    # Positive factors (good)
    if inputs["ExternalRiskEstimate"] >= 70:
        reasons.append("Your credit risk score is relatively strong.")
    if util_pct <= 30:
        reasons.append("Your credit card utilization appears healthy (lower financial strain).")
    if inputs["NumInqLast6M"] <= 1:
        reasons.append("You have limited recent credit inquiries.")
    if inputs["MSinceMostRecentDelq"] >= 24:
        reasons.append("It has been a long time since your most recent missed payment.")
    if inputs["CreditHistoryYears"] >= 5:
        reasons.append("You have a reasonably established credit history.")

    # Risk factors (bad)
    md12 = inputs["MaxDelq2PublicRecLast12M"]
    if md12 in [0, 1, 2, 3, 4]:
        reasons.append("Recent delinquency signals in the last 12 months increase perceived risk.")
        tips.append("Maintain on-time payments to increase the months since the last delinquency.")
    if util_pct > 35:
        tips.append("Reduce revolving balances to lower utilization.")
    if inputs["NumInqLast6M"] >= 3:
        tips.append("Avoid new credit applications/inquiries for 6–12 months if possible.")
    if inputs["ExternalRiskEstimate"] < 50:
        tips.append("Improve overall credit standing (e.g., on-time payments and lower utilization).")
    if inputs["CreditHistoryYears"] < 2:
        tips.append("Build credit history length through consistent responsible account management.")

    # De-duplicate while preserving order
    def dedup(xs):
        seen = set()
        out = []
        for x in xs:
            if x not in seen:
                out.append(x)
                seen.add(x)
        return out

    reasons = dedup(reasons)
    tips = dedup(tips)

    # Keep it short for applicants
    reasons = reasons[:4] if len(reasons) > 0 else ["We did not detect strong risk signals based on the provided information."]
    tips = tips[:3] if len(tips) > 0 else ["Continue maintaining a stable financial profile and provide complete documentation."]

    return reasons, tips

# =========================
# (C) Applicant-facing UI
# =========================
st.title("HELOC Application Pre-Screening (Prototype)")
st.caption("A simple pre-screening tool for applicants. This is **not** the final decision; a loan officer review may still be required.")

st.subheader("1) Provide a few simple details")

ExternalRiskEstimate = st.slider("Credit risk score (higher is better)", 0, 100, 70, 1)

CreditHistoryYears = st.slider("Credit history length (years)", 0, 30, 8, 1)

MSinceMostRecentDelq = st.slider("Months since your most recent missed payment", 0, 120, 36, 1)

util_pct = st.slider("Credit card utilization / burden (%)", 0, 100, 25, 1)
NetFractionRevolvingBurden = util_pct / 100.0

NumInqLast6M = st.slider("New credit applications/inquiries in the last 6 months", 0, 10, 1, 1)

MaxDelq2PublicRecLast12M = st.selectbox(
    "Worst delinquency status in the last 12 months",
    options=[
        (7, "Current / never delinquent"),
        (4, "30 days delinquent"),
        (3, "60 days delinquent"),
        (2, "90 days delinquent"),
        (1, "120+ days delinquent"),
        (0, "Derogatory comment"),
        (5, "Unknown / not sure"),
        (6, "Unknown / not sure"),
        (8, "Other"),
        (9, "Other"),
    ],
    format_func=lambda x: x[1],
    index=0
)[0]

inputs = {
    "ExternalRiskEstimate": ExternalRiskEstimate,
    "CreditHistoryYears": CreditHistoryYears,
    "MSinceMostRecentDelq": MSinceMostRecentDelq,
    "NetFractionRevolvingBurden": NetFractionRevolvingBurden,
    "NumInqLast6M": NumInqLast6M,
    "MaxDelq2PublicRecLast12M": MaxDelq2PublicRecLast12M,
}

st.divider()

st.subheader("2) Screening result")

# You can tune this later with model performance + business risk appetite
DENY_THRESHOLD = 0.80  # higher threshold reduces false negatives (wrongly rejecting good applicants)

prob_bad = predict_prob_bad(inputs)

# Applicant-friendly decision language
if prob_bad >= DENY_THRESHOLD:
    decision = "Not Approved for Fast-Track (Please improve and/or request manual review)"
else:
    decision = "Pass Pre-Screening (Proceed to manual review)"

st.markdown(f"### **Result: {decision}**")

# Explain reasons in plain language
reasons, tips = build_reasons(inputs)

st.markdown("**Why this result? (Key factors)**")
for r in reasons:
    st.write(f"- {r}")

st.markdown("**What you can do next (Suggestions)**")
for t in tips:
    st.write(f"- {t}")

with st.expander("Optional: show risk probability (for demo / internal use)"):
    st.write(f"Estimated probability of **bad outcome (bad = 1)**: **{prob_bad:.1%}**")
    st.write(f"(Internal deny threshold: {DENY_THRESHOLD:.0%})")

st.divider()
st.caption(
    "Disclaimer: This prototype provides a pre-screening recommendation and does not replace final human review. "
    "Final lending decisions remain subject to bank policy and regulatory requirements."
)
