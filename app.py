import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="ESCC Prognostic Risk Calculator", page_icon="🧬", layout="wide")

st.title("🧬 ESCC Prognostic Risk Stratification Tool")
st.markdown("""
**Privacy-Preserving Generative AI Framework for Esophageal Squamous Cell Carcinoma**  
Based on the core protein-coding signature: **ZNF34, LUC7L2, ZNF710**

This tool calculates a prognostic risk score using the three conserved genes validated across RNA-seq and microarray platforms.
""")

st.info("""
**How to use:**  
1. Enter expression values (log2 or raw; Z-score recommended if available).  
2. Choose weighting method.  
3. Get risk score and high/low classification.
""")

# Weights from XGBoost Gain importance (normalized)
weights = {
    "ZNF34": 0.009334,
    "LUC7L2": 0.008668,
    "ZNF710": 0.008221
}
total_w = sum(weights.values())
norm_weights = {k: v / total_w for k, v in weights.items()}

col1, col2, col3 = st.columns(3)

with col1:
    znf34 = st.number_input("ZNF34 expression", value=0.0, format="%.4f", help="Enter Z-score or log2(FPKM+1)")
with col2:
    luc7l2 = st.number_input("LUC7L2 expression", value=0.0, format="%.4f")
with col3:
    znf710 = st.number_input("ZNF710 expression", value=0.0, format="%.4f")

weighting = st.radio("Risk score weighting", ["Equal weight (recommended for external use)", "XGBoost Gain-weighted"], horizontal=True)

# Calculate risk score
if weighting == "Equal weight (recommended for external use)":
    risk_score = (znf34 + luc7l2 + znf710) / 3
    method_note = "Equal-weighted average of the three genes"
else:
    risk_score = (
        znf34 * norm_weights["ZNF34"] +
        luc7l2 * norm_weights["LUC7L2"] +
        znf710 * norm_weights["ZNF710"]
    )
    method_note = "Weighted by XGBoost Gain importance (ZNF34: 35.6%, LUC7L2: 33.1%, ZNF710: 31.3%)"

# Classification (threshold = 0 for Z-score based; users can adjust)
threshold = st.slider("Risk threshold (0 = median for Z-score input)", min_value=-2.0, max_value=2.0, value=0.0, step=0.1)

risk_group = "High-risk" if risk_score > threshold else "Low-risk"
color = "#e74c3c" if risk_group == "High-risk" else "#27ae60"

st.markdown("---")
st.subheader("Results")

c1, c2 = st.columns(2)
with c1:
    st.metric("Risk Score", f"{risk_score:.4f}")
with c2:
    st.markdown(f"**Predicted Group:** <span style='color:{color}; font-size:24px; font-weight:bold'>{risk_group}</span>", unsafe_allow_html=True)

st.caption(f"Method: {method_note} | Threshold: {threshold}")

# Simple visualization
fig = go.Figure(go.Indicator(
    mode="gauge+number",
    value=risk_score,
    domain={'x': [0, 1], 'y': [0, 1]},
    title={'text': "Risk Score"},
    gauge={
        'axis': {'range': [-3, 3]},
        'bar': {'color': color},
        'steps': [
            {'range': [-3, threshold], 'color': "#d5f5e3"},
            {'range': [threshold, 3], 'color': "#fadbd8"}
        ],
        'threshold': {
            'line': {'color': "black", 'width': 4},
            'thickness': 0.75,
            'value': threshold
        }
    }
))
st.plotly_chart(fig, use_container_width=True)

st.markdown("""
---
**Notes**  
- Recommended input: Z-score transformed expression values (as performed in the original study).  
- Higher score indicates higher predicted risk.  
- This simplified 3-gene signature was validated on the independent GSE53625 SuperSeries (log-rank *P* = 0.035).  
- For research use only. Not a clinical diagnostic tool.

**Citation**  
Chu F, Bai B, et al. A Privacy-Preserving Generative AI Framework for Prognostic Risk Stratification in Esophageal Squamous Cell Carcinoma. *Computational and Structural Biotechnology Journal*.
""")