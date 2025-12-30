import streamlit as st
import numpy as np
import joblib
import os
import time

# ================= CONFIG =================
MODEL_PATH = "/models/sgd.joblib"

st.set_page_config(
    page_title="CO₂ Predictor",
    layout="wide"
)

# ================= STYLE =================
st.markdown("""
<style>
.card {
    background-color: #161B22;
    padding: 25px;
    border-radius: 12px;
}
.big {
    font-size: 36px;
    font-weight: 700;
}
.result {
    font-size: 30px;
    color: #00E676;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

# ================= HEADER =================
st.markdown('<div class="big">🚗 Prédiction des émissions de CO₂</div>', unsafe_allow_html=True)
st.markdown("Estimation instantanée basée sur un modèle ML entraîné en streaming")
st.markdown("---")

# ================= LOAD MODEL =================
@st.cache_resource(show_spinner=True)
def load_model(path):
    return joblib.load(path)

if not os.path.exists(MODEL_PATH):
    st.error("❌ Modèle indisponible. Attendez l’entraînement Spark.")
    st.stop()

model = load_model(MODEL_PATH)

# ================= FORM =================
with st.form("prediction_form"):
    st.markdown("### 🔧 Caractéristiques du véhicule")

    col1, col2 = st.columns(2)

    with col1:
        engine_size = st.number_input("🔹 Taille du moteur (L)", 0.0, 10.0, 1.5, 0.1)
        cylinders = st.number_input("🔹 Cylindres", 1, 16, 4)
        fuel_city = st.number_input("🏙️ Conso ville (L/100km)", 0.0, 30.0, 8.0, 0.1)

    with col2:
        fuel_hwy = st.number_input("🛣️ Conso autoroute (L/100km)", 0.0, 30.0, 6.0, 0.1)
        fuel_comb = st.number_input("⚖️ Conso combinée (L/100km)", 0.0, 30.0, 7.0, 0.1)
        fuel_type = st.selectbox("⛽ Type de carburant", ["D", "E", "N", "X", "Z"])

    submitted = st.form_submit_button("🔮 Lancer la prédiction")

# ================= PREDICT =================
fuel_encoding = {
    "D": [1, 0, 0, 0, 0],
    "E": [0, 1, 0, 0, 0],
    "N": [0, 0, 1, 0, 0],
    "X": [0, 0, 0, 1, 0],
    "Z": [0, 0, 0, 0, 1]
}

if submitted:
    X = np.array([[engine_size, cylinders, fuel_city, fuel_hwy, fuel_comb, *fuel_encoding[fuel_type]]])

    pred = model.predict(X)[0]

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### 🌱 Résultat de la prédiction")
    st.markdown(f'<div class="result">{pred:.2f} g/km CO₂</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ================= FOOTER =================
st.markdown("---")
if st.button("🔄 Recharger le modèle"):
    st.cache_resource.clear()
    time.sleep(1)
    st.rerun()
