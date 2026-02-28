import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
import pytz
from sklearn.ensemble import RandomForestClassifier
from scipy.stats import norm

# --- 1. SETUP DE INFRAESTRUTURA E ESTILIZAÇÃO ---
st.set_page_config(page_title="AURAXIS V65 - SINGULARITY", layout="wide", page_icon="🧠")

st.markdown("""
    <style>
    .stApp { background-color: #01040a; color: #c9d1d9; font-family: 'Inter', sans-serif; }
    .price-hero { font-family: 'JetBrains Mono', monospace; font-size: 5rem; font-weight: 800; text-align: center; color: #ffffff; margin-bottom: -10px; }
    .universe-box { padding: 20px; border-radius: 12px; border: 1px solid #30363d; margin-bottom: 15px; background: rgba(13, 17, 23, 0.8); }
    .u1-active { border-left: 8px solid #238636; box-shadow: 0 0 20px rgba(35,134,54,0.1); }
    .u2-active { border-left: 8px solid #1f6feb; box-shadow: 0 0 20px rgba(31,111,235,0.1); }
    .surf-mode { background: linear-gradient(90deg, #0d1117, #1e1b4b); border: 2px solid #f1e05a; text-align: center; padding: 12px; border-radius: 10px; color: #f1e05a; font-weight: bold; margin-bottom: 20px; animation: glow 2s infinite; }
    @keyframes glow { 0% { opacity: 0.8; } 50% { opacity: 1; } 100% { opacity: 0.8; } }
    .metric-card { background: #0d1117; border: 1px solid #30363d; padding: 10px; border-radius: 8px; text-align: center; }
    .waiting { border: 1px dashed #484f58; opacity: 0.4; text-align: center; padding: 30px; border-radius: 10px; }
    </style>
""", unsafe_allow_html=True)

# --- 2. MOTOR PROBABILÍSTICO (MONTE CARLO & BAYES) ---
@st.cache_data(ttl=60)
def fetch_and_refine_data(ticker):
    df = yf.download(ticker, period="2d", interval="1m", progress=False)
    # Fragmentação simbólica (Amostragem de Qualidade)
    df['Returns'] = df['Close'].pct_change()
    return df.dropna()

def run_monte_carlo(current_price, volatility, iterations=1000, steps=60):
    # Simula 1000 caminhos para os próximos 60 minutos
    returns = np.random.normal(0, volatility, (iterations, steps))
    price_paths = current_price * (1 + returns).cumprod(axis=1)
    return price_paths

def bayesian_update(prior_prob, flow_strength):
    # Ajusta a probabilidade baseada no fluxo institucional (evidência)
    evidence = np.clip(flow_strength / 2, 0.1, 0.9)
    posterior = (evidence * prior_prob) / ((evidence * prior_prob) + ((1 - evidence) * (1 - prior_prob)))
    return posterior

# --- 3. MOTOR DE INTELIGÊNCIA ARTIFICIAL ---
def run_ia_model(df):
    # Features básicas para o Classificador Random Forest
    df['SMA_10'] = df['Close'].rolling(10).mean()
    df['Z_Score'] = (df['Close'] - df['SMA_10']) / df['Close'].rolling(10).std()
    
    # Simulação de treinamento rápido (Amostragem de Qualidade)
    X = df[['Z_Score']].fillna(0).tail(100)
    y = np.where(df['Returns'].shift(-1) > 0, 1, 0)[-100:]
    
    model = RandomForestClassifier(n_estimators=50)
    model.fit(X, y)
    
    prob_ia = model.predict_proba(X.tail(1)) [0][1]
    return prob_ia

# --- 4. CORE EXECUTION ---
try:
    data = fetch_and_refine_data("EURUSD=X")
    if not data.empty:
        # Telemetria Base
        p_atual = data['Close'].iloc[-1]
        atr = (data['High'] - data['Low']).rolling(14).mean().iloc[-1]
        v_rel = data['Volume'].iloc[-1] / (data['Volume'].rolling(20).mean().iloc[-1] + 1e-9)
        
        # Inteligência Avançada
        confianca_ia = run_ia_model(data)
        
        # Monte Carlo para TP3
        paths = run_monte_carlo(p_atual, data['Returns'].std())
        mc_target = np.percentile(paths[:, -1], 75) # Convergência estatística
        
        # Bayes Update
        prob_final = bayesian_update(confianca_ia, v_rel)

        # Lógica de Gatilhos e Sucessão
        u1_gate = (confianca_ia > 0.65) and (v_rel < 1.5)
        u2_gate = (v_rel >= 1.5) or (confianca_ia > 0.60 and p_atual > data['Open'].iloc[-1] + (atr*0.3))
        
        # Modo Surfe
        is_surfing = u1_gate and u2_gate

        # --- INTERFACE VISUAL ---
        st.markdown(f"<div class='price-hero'>{p_atual:.5f}</div>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align:center; color:#8b949e;'>AURAXIS OS SINGULARITY | IA: {prob_final*100:.1f}%</p>", unsafe_allow_html=True)

        # Telemetria Superior
        c1, c2, c3, c4 = st.columns(4)
        c1.markdown(f"<div class='metric-card'><small>ESTAT. BAYES</small><br><span style='font-size:1.5rem; color:#10b981;'>{prob_final*100:.0f}%</span></div>", unsafe_allow_html=True)
        c2.markdown(f"<div class='metric-card'><small>MONTE CARLO (TP3)</small><br><span style='font-size:1.5rem; color:#3b82f6;'>{mc_target:.5f}</span></div>", unsafe_allow_html=True)
        c3.markdown(f"<div class='metric-card'><small>VOL. RELATIVO</small><br><span style='font-size:1.5rem;'>{v_rel:.2f}x</span></div>", unsafe_allow_html=True)
        c4.markdown(f"<div class='metric-card'><small>Z-SCORE</small><br><span style='font-size:1.5rem; color:#ef4444;'>{((p_atual - data['Close'].rolling(50).mean().iloc[-1])/data['Close'].rolling(50).std().iloc[-1]):.2f}</span></div>", unsafe_allow_html=True)

        if is_surfing:
            st.markdown("<div class='surf-mode'>🌊 MODO SURFE ATIVO: U1 potencializada por Monte Carlo + Fluxo U2</div>", unsafe_allow_html=True)

        col_u1, col_u2 = st.columns(2)

        # COLUNA U1 (SNIPER)
        with col_u1:
            if u1_gate or is_surfing:
                st.markdown(f"""<div class='universe-box u1-active'>
                    <h3 style='color:#10b981;'>U1: SNIPER</h3>
                    <p style='font-size:0.8rem; color:#8b949e;'>ESTADO: {"SURFANDO" if is_surfing else "LANÇADA"}</p>
                    <hr style='border-color:#30363d;'>
                    <small>TP3 ESTATÍSTICO (MC)</small>
                    <div style='font-size:1.8rem; font-weight:bold; color:#10b981;'>{max(mc_target, p_atual + (atr*5.5)):.5f}</div>
                    <small>SAFETY ZONE</small><div style='color:#ffffff;'>{p_atual + (atr*1.2):.5f}</div>
                    <small>STOP RÍGIDO</small><div style='color:#ef4444;'>{p_atual - (atr*2.5):.5f}</div>
                </div>""", unsafe_allow_html=True)
            else:
                st.markdown("<div class='waiting'><h3>AGUARDANDO U1</h3><p>Sniper fora de posição</p></div>", unsafe_allow_html=True)

        # COLUNA U2 (FLOW)
        with col_u2:
            if u2_gate:
                st.markdown(f"""<div class='universe-box u2-active'>
                    <h3 style='color:#1f6feb;'>U2: FLOW</h3>
                    <p style='font-size:0.8rem; color:#8b949e;'>ESTADO: FLUXO INSTITUCIONAL</p>
                    <hr style='border-color:#30363d;'>
                    <small>TP3 IMPULSO</small>
                    <div style='font-size:1.8rem; font-weight:bold; color:#1f6feb;'>{p_atual + (atr*3.5):.5f}</div>
                    <small>SAFETY ZONE</small><div style='color:#ffffff;'>{p_atual + (atr*0.6):.5f}</div>
                    <small>STOP TÉCNICO</small><div style='color:#ef4444;'>{p_atual - (atr*1.2):.5f}</div>
                </div>""", unsafe_allow_html=True)
            else:
                st.markdown("<div class='waiting'><h3>AGUARDANDO U2</h3><p>Aguardando transição de volume</p></div>", unsafe_allow_html=True)

        

        # FOOTER E SNAPSHOT
        st.markdown("---")
        if st.button("🏁 GERAR SNAPSHOT DE EFICIÊNCIA"):
            eficiencia = (mc_target - p_atual) * 10000
            st.success(f"Snapshot Final: Eficiência Probabilística de {eficiencia:.1f} pips.")

except Exception as e:
    st.info("Sincronizando campos neurais... Aguarde o próximo tick.")

st.markdown("""<meta http-equiv="refresh" content="60">""", unsafe_allow_html=True)
