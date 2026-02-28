import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from scipy.stats import norm
from datetime import datetime
import pytz

# --- CONFIGURAÇÃO DE UI TERMINAL ---
st.set_page_config(page_title="AURAXIS V32 - SOBERANO", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #050505; color: #e2e8f0; }
    .main-terminal { background: #0d1117; border: 1px solid #30363d; padding: 25px; border-radius: 20px; text-align: center; }
    .price-hero { font-family: monospace; font-size: 4rem; font-weight: 700; color: #ffffff; }
    .signal-card { padding: 20px; border-radius: 12px; margin-top: 10px; font-weight: bold; border-left: 8px solid; }
    </style>
""", unsafe_allow_html=True)

class AuraxisMind:
    def __init__(self, df):
        self.df = df
        
    def get_analysis(self):
        df = self.df.copy()
        last = df.iloc[-1]
        
        # 1. MÉTRICAS V1-V10 (Anatomia)
        body = last['Close'] - last['Open']
        range_tot = last['High'] - last['Low']
        wick_inf = min(last['Open'], last['Close']) - last['Low']
        wick_sup = last['High'] - max(last['Open'], last['Close'])
        
        # 2. ESTATÍSTICA (Z-Score)
        z = (last['Close'] - df['Close'].rolling(20).mean().iloc[-1]) / df['Close'].rolling(20).std().iloc[-1]
        
        # 3. MACHINE LEARNING (Random Forest)
        df['B'] = df['Close'] - df['Open']
        df['V'] = df['Volume'] / df['Volume'].rolling(20).mean()
        df['T'] = np.where(df['Close'].shift(-5) > df['Close'], 1, 0)
        train = df.dropna()
        model = RandomForestClassifier(n_estimators=30).fit(train[['B', 'V']][:-5], train['T'][:-5])
        prob_ml = model.predict_proba(train[['B', 'V']].iloc[[-1]])[0][1] * 100
        
        # 4. MONTE CARLO (Probabilidade Estocástica)
        returns = df['Close'].pct_change().dropna()
        mc = (np.array([last['Close'] * (1 + np.random.choice(returns, 15)).prod() for _ in range(100)]) > last['Close']).mean() * 100
        
        # 5. SÍNTESE BAYESIANA (Ajuste de Probabilidade Final)
        # ML atua como a evidência que atualiza a crença de Monte Carlo
        prob_final = (prob_ml * 0.6) + (mc * 0.4)
        
        return {"z": z, "v": last['Volume']/df['Volume'].rolling(20).mean().iloc[-1], "prob": prob_final, 
                "body": body, "w_inf": wick_inf, "w_sup": wick_sup, "range": range_tot}

# --- INTERFACE ---
try:
    data = yf.download("EURUSD=X", period="1d", interval="1m", progress=False)
    if not data.empty:
        intel = AuraxisMind(data).get_analysis()
        
        st.markdown(f"""
            <div class="main-terminal">
                <div style="font-size:0.7rem; color:#8b949e;">AURAXIS V32 SOBERANO</div>
                <div class="price-hero">{data['Close'].iloc[-1]:.5f}</div>
                <div style="display:flex; justify-content:center; gap:20px;">
                    <span>Z: {intel['z']:.2f}</span> | <span>VOL: {intel['v']:.2f}x</span> | <span>SCORE IA: {intel['prob']:.1f}%</span>
                </div>
            </div>
        """, unsafe_allow_html=True)

        

        # GATILHOS INTEGRADOS
        if intel['v'] > 1.2:
            # Absorção (V1+V30)
            if intel['w_inf'] > abs(intel['body']) * 1.5 and intel['z'] < -2:
                st.markdown('<div class="signal-card" style="border-color:#3b82f6; background:#3b82f615; color:#3b82f6;">ABSORÇÃO DE FUNDO: REVERSÃO PARA COMPRA</div>', unsafe_allow_html=True)
            
            # Impulso IA (ML+Bayes)
            if intel['prob'] > 75:
                st.markdown('<div class="signal-card" style="border-color:#10b981; background:#10b98115; color:#10b981;">CONFLUÊNCIA SOBERANA: IMPULSO DE ALTA</div>', unsafe_allow_html=True)
            elif intel['prob'] < 25:
                st.markdown('<div class="signal-card" style="border-color:#ef4444; background:#ef444415; color:#ef4444;">CONFLUÊNCIA SOBERANA: IMPULSO DE BAIXA</div>', unsafe_allow_html=True)

except:
    st.info("Sincronizando Córtex Neural...")

st.markdown("""<meta http-equiv="refresh" content="60">""", unsafe_allow_html=True)
