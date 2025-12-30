import streamlit as st
import json
import pandas as pd
import os
import time

# ================= CONFIG =================
METRICS_PATH = "/models/metrics.json"
REFRESH_SECONDS = 5

st.set_page_config(
    page_title="ML Model Monitoring",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ================= STYLE =================
st.markdown("""
<style>
body {
    background-color: #0E1117;
}
.big-title {
    font-size: 40px;
    font-weight: 700;
    color: #EAEAEA;
}
.sub-title {
    font-size: 18px;
    color: #AAAAAA;
}
.card {
    background-color: #161B22;
    padding: 20px;
    border-radius: 12px;
    box-shadow: 0px 0px 10px rgba(0,0,0,0.3);
}
.metric {
    font-size: 32px;
    font-weight: bold;
    color: #00E676;
}
.footer {
    color: #666;
    text-align: center;
    margin-top: 40px;
}
</style>
""", unsafe_allow_html=True)

# ================= HEADER =================
st.markdown('<div class="big-title">📊 Surveillance du modèle ML</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Évaluation en temps réel – Pipeline Spark & Kafka</div>', unsafe_allow_html=True)
st.markdown("---")

# ================= LOAD METRICS =================
if not os.path.exists(METRICS_PATH):
    st.warning("⏳ En attente des métriques générées par Spark…")
    st.stop()

with open(METRICS_PATH, "r") as f:
    metrics = json.load(f)

if not metrics.get("batch"):
    st.info("ℹ️ Aucun batch traité pour le moment.")
    st.stop()

df = pd.DataFrame(metrics)

# ================= KPI =================
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("📌 **Dernier RMSE**")
    st.markdown(f'<div class="metric">{df["rmse"].iloc[-1]:,.2f}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("📦 **Nombre de batches**")
    st.markdown(f'<div class="metric">{len(df)}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col3:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("⏱️ **Fréquence**")
    st.markdown(f'<div class="metric">{REFRESH_SECONDS}s</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("## 📈 Évolution du RMSE")

st.line_chart(
    df.set_index("batch")["rmse"],
    height=420
)

st.markdown(
    '<div class="footer">🔄 Rafraîchissement automatique toutes les 5 secondes</div>',
    unsafe_allow_html=True
)

time.sleep(REFRESH_SECONDS)
st.rerun()
