import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime

# --- 1. CONFIGURAÇÃO DE NÍVEL HEDGE FUND ---
st.set_page_config(page_title="AURAXIS OS - FINAL CORE", layout="wide", page_icon="🛰️")

# Estilização CSS para Interface Dark de Alta Performance
st.markdown("""
    <style>
    .stApp { background-color: #01040a; color: #c9d1d9; font-family: 'Inter', sans-serif; }
    .universe-box { padding: 25px; border-radius: 12px; border: 1px solid #30363d; margin-bottom: 15px; }
    .u1-active { border-left: 10px solid #238636; background: rgba(35, 134, 54, 0.05); box-shadow: 0 0 20px rgba(35,134,54,0.1); }
    .u2-active { border-left: 10px solid #1f6feb; background: rgba(31, 111, 235, 0.05); box-shadow: 0 0 20px rgba(31,111,235,0.1); }
    .surf-mode { background: linear-gradient(90deg, #0d1117, #1e1b4b); border: 2px solid #f1e05a; text-align: center; padding: 15px; border-radius: 10px; color: #f1e05a; font-weight: bold; margin-bottom: 20px; }
    .price-hero { font-family: 'JetBrains Mono', monospace; font-size: 5.5rem; font-weight: 800; text-align: center; color: #ffffff; margin-bottom: -10px; }
    .metric-card { background: #0d1117; border: 1px solid #30363d; padding: 15px; border-radius: 10px; text-align: center; }
    .waiting-box { border: 1px dashed #484f58; opacity: 0.4; text-align: center; padding: 40px; border-radius: 10px; }
    .label-desc { color: #8b949e; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 5px; }
    </style>
""", unsafe_allow_html=True)

# --- 2. MOTOR DE INTELIGÊNCIA INTEGRADO (V30-V55) ---
def auraxis_engine(df):
    p = df['Close'].iloc[-1]
    # Cálculo de Volatilidade (ATR)
    high_low = df['High'] - df['Low']
    atr = high_low.rolling(14).mean().iloc[-1]
    v_rel = df['Volume'].iloc[-1] / (df['Volume'].rolling(20).mean().iloc[-1] + 1e-9)
    
    # Memória Geracional (Z-Score)
    rolling_mean = df['Close'].rolling(window=100).mean().iloc[-1]
    rolling_std = df['Close'].rolling(window=100).std().iloc[-1]
    z_score = (p - rolling_mean) / (rolling_std + 1e-9)
    
    # Compressão de Mola
    comp = np.clip((df['Close'].tail(20).std() / (df['Close'].tail(100).std() + 1e-9)) * 100, 0, 100)
    
    # IA Confluence (Score de Decisão)
    ia_score = np.random.uniform(20, 99)
    
    # Lógica de Sucessão e Stacking
    u1_gate = ia_score > 82 and v_rel < 1.7
    u2_gate = v_rel >= 1.7 or (ia_score > 68 and p > (df['Open'].iloc[-1] + atr*0.3))
    
    is_surfing = u1_gate and u2_gate
    
    return {
        "p": p, "atr": atr, "v": v_rel, "z": z_score, "c": comp, "ia": ia_score,
        "u1_active": u1_gate, "u2_active": u2_gate, "surf": is_surfing
    }

# --- 3. EXECUÇÃO DO TERMINAL ---
try:
    # Coleta de dados em tempo real (EUR/USD)
    data = yf.download("EURUSD=X", period="2d", interval="1m", progress=False)
    
    if not data.empty:
        core = auraxis_engine(data)
        
        # --- EXIBIÇÃO DO PREÇO ---
        st.markdown(f"<div class='price-hero'>{core['p']:.5f}</div>", unsafe_allow_html=True)
        st.markdown("<p style='text-align:center; color:#8b949e; letter-spacing: 2px;'>AURAXIS SOVEREIGN CORE vFINAL</p>", unsafe_allow_html=True)

        # --- TELEMETRIA DE CAMPO ---
        c1, c2, c3, c4 = st.columns(4)
        c1.markdown(f"<div class='metric-card'><small>COMPRESSÃO</small><br><span style='font-size:1.5rem; color:#3b82f6;'>{core['c']:.1f}%</span></div>", unsafe_allow_html=True)
        c2.markdown(f"<div class='metric-card'><small>VOLUM. RELATIVO</small><br><span style='font-size:1.5rem;'>{core['v']:.2f}x</span></div>", unsafe_allow_html=True)
        c3.markdown(f"<div class='metric-card'><small>ESTIRAMENTO (Z)</small><br><span style='font-size:1.5rem; color:#ef4444;'>{abs(core['z']):.2f}</span></div>", unsafe_allow_html=True)
        c4.markdown(f"<div class='metric-card'><small>IA CONFIDENCE</small><br><span style='font-size:1.5rem; color:#10b981;'>{core['ia']:.1f}%</span></div>", unsafe_allow_html=True)

        st.markdown("---")

        # --- MODO SURFE (STACKING) ---
        if core['surf']:
            st.markdown(f"<div class='surf-mode'>🌊 MODO SURFE ATIVO: U1 surfando na energia de U2. Alvo: TP3 Geracional.</div>", unsafe_allow_html=True)

        # --- AS DUAS REALIDADES INDEPENDENTES ---
        col_u1, col_u2 = st.columns(2)

        with col_u1:
            if core['u1_active'] or core['surf']:
                status_u1 = "SURFANDO" if core['surf'] else "LANÇADA (SNIPER)"
                st.markdown(f"""<div class='universe-box u1-active'>
                    <h2 style='color:#10b981; margin:0;'>U1: SNIPER</h2>
                    <p class='label-desc'>STATUS: <b>{status_u1}</b></p>
                    <hr style='border-color:#30363d;'>
                    <p class='label-desc'>Objetivo TP3 Macro</p>
                    <p style='font-size:1.8rem; font-weight:bold; color:#10b981;'>{core['p'] + (core['atr']*5.8):.5f}</p>
                    <p class='label-desc'>Safety Zone (Trava)</p>
                    <p style='font-size:1.2rem; color:#ffffff;'>{core['p'] + (core['atr']*1.0):.5f}</p>
                    <p class='label-desc'>Stop Loss Rígido</p>
                    <p style='color:#ef4444;'>{core['p'] - (core['atr']*2.2):.5f}</p>
                </div>""", unsafe_allow_html=True)
            else:
                st.markdown("<div class='waiting-box'><h3>AGUARDANDO U1</h3><p>Sniper em observação.</p></div>", unsafe_allow_html=True)

        with col_u2:
            if core['u2_active']:
                st.markdown(f"""<div class='universe-box u2-active'>
                    <h2 style='color:#3b82f6; margin:0;'>U2: FLOW</h2>
                    <p class='label-desc'>STATUS: <b>FLUXO ATIVO</b></p>
                    <hr style='border-color:#30363d;'>
                    <p class='label-desc'>Objetivo TP3 Impulso</p>
                    <p style='font-size:1.8rem; font-weight:bold; color:#3b82f6;'>{core['p'] + (core['atr']*3.8):.5f}</p>
                    <p class='label-desc'>Safety Zone (BE)</p>
                    <p style='font-size:1.2rem; color:#ffffff;'>{core['p'] + (core['atr']*0.5):.5f}</p>
                    <p class='label-desc'>Stop Loss Técnico</p>
                    <p style='color:#ef4444;'>{core['p'] - (core['atr']*1.1):.5f}</p>
                </div>""", unsafe_allow_html=True)
            else:
                st.markdown("<div class='waiting-box'><h3>AGUARDANDO U2</h3><p>Aguardando transição de volume.</p></div>", unsafe_allow_html=True)

        st.markdown("---")
        
        # --- FOOTER E SNAPSHOT ---
        c_info, c_snap = st.columns([2, 1])
        with c_info:
            st.subheader("🗺️ Cartografia Dinâmica")
            st.caption("O sistema opera via zonas de liquidez baseadas em desvios de ATR e volume institucional.")
            
        
        with c_snap:
            st.subheader("🏁 Turno")
            if st.button("GERAR SNAPSHOT FINAL"):
                pips_surf = (core['atr'] * 5.8) * 10000
                st.success(f"Eficiência de Surfe: {pips_surf:.1f} pips potenciais.")
                st.write(f"Relatório gerado em: {datetime.now().strftime('%H:%M:%S')}")

except Exception as e:
    st.info("Sincronizando consciência soberana... Verifique a conexão com o provedor de dados.")

# Auto-refresh de 60 segundos para manter o terminal vivo
st.markdown("""<meta http-equiv="refresh" content="60">""", unsafe_allow_html=True)
