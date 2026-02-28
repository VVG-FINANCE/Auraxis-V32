import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
from sklearn.ensemble import RandomForestClassifier
from scipy.stats import norm

# --- 1. SETUP DE INFRAESTRUTURA E ESTILIZAÇÃO ---
st.set_page_config(page_title="AURAXIS V65.5 - SINGULARITY", layout="wide", page_icon="🧠")

st.markdown("""
    <style>
    .stApp { background-color: #01040a; color: #c9d1d9; font-family: 'Inter', sans-serif; }
    .price-hero { font-family: 'JetBrains Mono', monospace; font-size: 5rem; font-weight: 800; text-align: center; color: #ffffff; margin-bottom: -10px; }
    .universe-box { padding: 20px; border-radius: 12px; border: 1px solid #30363d; margin-bottom: 15px; background: rgba(13, 17, 23, 0.8); transition: 0.3s; }
    .u1-active { border-left: 8px solid #238636; box-shadow: 0 0 20px rgba(35,134,54,0.1); }
    .u2-active { border-left: 8px solid #1f6feb; box-shadow: 0 0 20px rgba(31,111,235,0.1); }
    .saturated { border-left: 8px solid #f1e05a !important; background: rgba(241, 224, 90, 0.05) !important; }
    .surf-mode { background: linear-gradient(90deg, #0d1117, #1e1b4b); border: 2px solid #f1e05a; text-align: center; padding: 12px; border-radius: 10px; color: #f1e05a; font-weight: bold; margin-bottom: 20px; animation: glow 2s infinite; }
    @keyframes glow { 0% { opacity: 0.8; } 50% { opacity: 1; } 100% { opacity: 0.8; } }
    .metric-card { background: #0d1117; border: 1px solid #30363d; padding: 10px; border-radius: 8px; text-align: center; }
    .waiting { border: 1px dashed #484f58; opacity: 0.4; text-align: center; padding: 30px; border-radius: 10px; }
    </style>
""", unsafe_allow_html=True)

# --- 2. FERRAMENTAS NEURAIS (SATURAÇÃO & ESPECTRO) ---
def calculate_saturation(df):
    # Lei de Esforço vs Resultado: Volume / Delta de Preço
    delta_price = abs(df['Close'].diff().iloc[-1]) + 1e-9
    volume = df['Volume'].iloc[-1]
    effort_result = volume / delta_price
    avg_effort = (df['Volume'] / (abs(df['Close'].diff()) + 1e-9)).rolling(20).mean().iloc[-1]
    
    # Saturação se o esforço for 2.5x maior que a média (Exaustão)
    is_saturated = effort_result > (avg_effort * 2.5)
    return effort_result, is_saturated

def calculate_spectrum(df):
    # Simulação de Espectro de Frequência (Variação de Volatilidade de curtíssimo prazo)
    vol_hertz = df['Returns'].tail(10).std() * 10000
    is_high_freq = vol_hertz > df['Returns'].rolling(50).std().iloc[-1] * 15000
    return vol_hertz, is_high_freq

# --- 3. MOTORES PROBABILÍSTICOS (MONTE CARLO, BAYES, IA) ---
@st.cache_data(ttl=60)
def fetch_and_refine_data(ticker):
    df = yf.download(ticker, period="2d", interval="1m", progress=False)
    df['Returns'] = df['Close'].pct_change()
    return df.dropna()

def run_monte_carlo(current_price, volatility, iterations=1000, steps=60):
    returns = np.random.normal(0, volatility, (iterations, steps))
    price_paths = current_price * (1 + returns).cumprod(axis=1)
    return price_paths

def bayesian_update(prior_prob, flow_strength):
    evidence = np.clip(flow_strength / 2, 0.1, 0.9)
    posterior = (evidence * prior_prob) / ((evidence * prior_prob) + ((1 - evidence) * (1 - prior_prob)))
    return posterior

def run_ia_model(df):
    df['SMA_10'] = df['Close'].rolling(10).mean()
    df['Z_Score'] = (df['Close'] - df['SMA_10']) / (df['Close'].rolling(10).std() + 1e-9)
    X = df[['Z_Score']].fillna(0).tail(100)
    y = np.where(df['Returns'].shift(-1) > 0, 1, 0)[-100:]
    model = RandomForestClassifier(n_estimators=50)
    model.fit(X, y)
    return model.predict_proba(X.tail(1))[0][1]

# --- 4. EXECUÇÃO CORE ---
try:
    data = fetch_and_refine_data("EURUSD=X")
    if not data.empty:
        p_atual = data['Close'].iloc[-1]
        atr = (data['High'] - data['Low']).rolling(14).mean().iloc[-1]
        v_rel = data['Volume'].iloc[-1] / (data['Volume'].rolling(20).mean().iloc[-1] + 1e-9)
        
        # Novas Métricas Neurais
        effort, saturated = calculate_saturation(data)
        freq_hz, high_freq = calculate_spectrum(data)
        
        # IA e Probabilidades
        confianca_ia = run_ia_model(data)
        paths = run_monte_carlo(p_atual, data['Returns'].std())
        mc_target = np.percentile(paths[:, -1], 75)
        prob_final = bayesian_update(confianca_ia, v_rel)

        # Gatilhos
        u1_gate = (confianca_ia > 0.65) and (v_rel < 1.5)
        u2_gate = (v_rel >= 1.5) or (confianca_ia > 0.60 and p_atual > data['Open'].iloc[-1] + (atr*0.3))
        is_surfing = u1_gate and u2_gate

        # --- INTERFACE ---
        st.markdown(f"<div class='price-hero'>{p_atual:.5f}</div>", unsafe_allow_html=True)
        
        # Painel de Espectro/Saturação Superior
        c1, c2, c3, c4 = st.columns(4)
        c1.markdown(f"<div class='metric-card'><small>ESPECTRO (Hz)</small><br><span style='font-size:1.5rem; color:{'#f1e05a' if high_freq else '#ffffff'};'>{freq_hz:.1f}</span></div>", unsafe_allow_html=True)
        c2.markdown(f"<div class='metric-card'><small>SATURAÇÃO</small><br><span style='font-size:1.5rem; color:{'#ef4444' if saturated else '#10b981'};'>{'CRÍTICA' if saturated else 'NORMAL'}</span></div>", unsafe_allow_html=True)
        c3.markdown(f"<div class='metric-card'><small>PROB. BAYES</small><br><span style='font-size:1.5rem; color:#10b981;'>{prob_final*100:.1f}%</span></div>", unsafe_allow_html=True)
        c4.markdown(f"<div class='metric-card'><small>CONVERGÊNCIA MC</small><br><span style='font-size:1.5rem; color:#3b82f6;'>{mc_target:.5f}</span></div>", unsafe_allow_html=True)

        if is_surfing:
            st.markdown("<div class='surf-mode'>🌊 MODO SURFE ATIVO: U1 potencializada por Stacking Neural</div>", unsafe_allow_html=True)
        if saturated:
            st.warning("⚠️ SATURAÇÃO DETECTADA: Volume alto sem deslocamento de preço. Possível absorção/reversão.")

        col_u1, col_u2 = st.columns(2)

        # U1: SNIPER
        with col_u1:
            u1_class = "universe-box u1-active" + (" saturated" if saturated else "")
            if u1_gate or is_surfing:
                st.markdown(f"""<div class='{u1_class}'>
                    <h3 style='color:#10b981;'>U1: SNIPER</h3>
                    <p style='font-size:0.8rem; color:#8b949e;'>{"EXAUSTÃO POSSÍVEL" if saturated else "ESTADO: LANÇADA"}</p>
                    <hr style='border-color:#30363d;'>
                    <small>TP3 ESTATÍSTICO (MC)</small>
                    <div style='font-size:1.8rem; font-weight:bold; color:#10b981;'>{max(mc_target, p_atual + (atr*5.5)):.5f}</div>
                    <small>SAFETY ZONE (PROTEÇÃO)</small><div style='color:#ffffff;'>{p_atual + (atr*1.2):.5f}</div>
                    <small>STOP RÍGIDO</small><div style='color:#ef4444;'>{p_atual - (atr*2.5):.5f}</div>
                </div>""", unsafe_allow_html=True)
            else:
                st.markdown("<div class='waiting'><h3>AGUARDANDO U1</h3></div>", unsafe_allow_html=True)

        # U2: FLOW
        with col_u2:
            u2_class = "universe-box u2-active" + (" saturated" if saturated else "")
            if u2_gate:
                st.markdown(f"""<div class='{u2_class}'>
                    <h3 style='color:#1f6feb;'>U2: FLOW</h3>
                    <p style='font-size:0.8rem; color:#8b949e;'>{"SATURAÇÃO DE FLUXO" if saturated else "ESTADO: MOMENTUM"}</p>
                    <hr style='border-color:#30363d;'>
                    <small>TP3 IMPULSO</small>
                    <div style='font-size:1.8rem; font-weight:bold; color:#1f6feb;'>{p_atual + (atr*3.5):.5f}</div>
                    <small>SAFETY ZONE</small><div style='color:#ffffff;'>{p_atual + (atr*0.6):.5f}</div>
                    <small>STOP TÉCNICO</small><div style='color:#ef4444;'>{p_atual - (atr*1.2):.5f}</div>
                </div>""", unsafe_allow_html=True)
            else:
                st.markdown("<div class='waiting'><h3>AGUARDANDO U2</h3></div>", unsafe_allow_html=True)

        st.markdown("---")
        if st.button("🏁 GERAR SNAPSHOT NEURAL"):
            st.success(f"Eficiência MC: {(mc_target-p_atual)*10000:.1f} pips | Espectro: {freq_hz:.1f} Hz")

except Exception as e:
    st.info("Sincronizando campos neurais e espectrais...")

st.markdown("""<meta http-equiv="refresh" content="60">""", unsafe_allow_html=True)
