import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import requests
from sklearn.ensemble import RandomForestClassifier
from datetime import datetime

# --- CONFIGURAÇÃO DE ALTA PERFORMANCE ---
st.set_page_config(page_title="AURAXIS V32 SOBERANO - DUAL CORE", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #050505; color: #e2e8f0; }
    .main-card { background: #0d1117; border: 1px solid #30363d; padding: 25px; border-radius: 20px; text-align: center; }
    .price-hero { font-family: monospace; font-size: 4.5rem; font-weight: 700; color: #ffffff; margin: 0; }
    .signal-active { padding: 15px; border-radius: 12px; margin-top: 10px; font-weight: bold; border-left: 10px solid; }
    .metric-box { background: #161b22; padding: 10px; border-radius: 10px; border: 1px solid #30363d; }
    </style>
""", unsafe_allow_html=True)

# --- SIDEBAR DE SEGURANÇA ---
with st.sidebar:
    st.header("🛡️ Painel de Redundância")
    api_key = st.text_input("Alpha Vantage API Key (Opcional):", type="password", help="Para diminuir o delay do preço vivo.")
    st.markdown("---")
    st.write("Versão: V32.5 Sovereign")
    st.write("Status: Inteligência Ativa")

class AuraxisTotalEngine:
    def __init__(self, df):
        self.df = df
        self.last = df.iloc[-1]
        
    def process_intelligence(self):
        df = self.df.copy()
        
        # 1. ANATOMIA V1 (Vetores de Força)
        body = self.last['Close'] - self.last['Open']
        wick_inf = min(self.last['Open'], self.last['Close']) - self.last['Low']
        wick_sup = self.last['High'] - max(self.last['Open'], self.last['Close'])
        
        # 2. Z-SCORE V15 (Exaustão Estatística)
        m20 = df['Close'].rolling(20).mean().iloc[-1]
        s20 = df['Close'].rolling(20).std().iloc[-1]
        z = (self.last['Close'] - m20) / (s20 + 1e-9)
        
        # 3. VOLUME V25 (Filtro Institucional)
        v_rel = self.last['Volume'] / (df['Volume'].rolling(20).mean().iloc[-1] + 1e-9)
        
        # 4. MONTE CARLO V25 (Projeção Estocástica - 100 Caminhos)
        returns = df['Close'].pct_change().dropna()
        mc_results = [self.last['Close'] * (1 + np.random.choice(returns, 15)).prod() for _ in range(100)]
        prob_mc = (np.array(mc_results) > self.last['Close']).mean() * 100
        
        # 5. MACHINE LEARNING V31 (Random Forest Classifier)
        df['Feat_B'] = df['Close'] - df['Open']
        df['Feat_V'] = df['Volume'] / df['Volume'].rolling(20).mean()
        df['Target'] = np.where(df['Close'].shift(-5) > df['Close'], 1, 0)
        train = df.dropna()
        model = RandomForestClassifier(n_estimators=30).fit(train[['Feat_B', 'Feat_V']][:-5], train['Target'][:-5])
        prob_ml = model.predict_proba(train[['Feat_B', 'Feat_V']].iloc[[-1]])[0][1] * 100
        
        # 6. SÍNTESE BAYESIANA (Fusão MC + ML)
        final_prob = (prob_ml * 0.6) + (prob_mc * 0.4)
        
        return {"z": z, "v": v_rel, "prob": final_prob, "body": body, "w_inf": wick_inf, "w_sup": wick_sup, "mc": prob_mc, "ml": prob_ml}

# --- FUNÇÃO DUAL-CORE (Alpha Vantage) ---
def get_alpha_price(key):
    try:
        url = f'https://www.alphavantage.co/query?function=CURRENCY_EXCHANGE_RATE&from_currency=EUR&to_currency=USD&apikey={key}'
        data = requests.get(url).json()
        return float(data['Realtime Currency Exchange Rate']['5. Exchange Rate'])
    except:
        return None

# --- CICLO DE EXECUÇÃO ---
try:
    # Coleta Yahoo (Base Histórica para a IA)
    data_hist = yf.download("EURUSD=X", period="1d", interval="1m", progress=False)
    
    if not data_hist.empty:
        # Tenta Preço Vivo Alpha Vantage
        live_p = get_alpha_price(api_key) if api_key else None
        p_final = live_p if live_p else data_hist['Close'].iloc[-1]
        fonte = "🟢 DUAL-CORE" if live_p else "🟡 YAHOO-ONLY"
        
        # Processa a Mente do Sistema
        engine = AuraxisTotalEngine(data_hist)
        m = engine.process_intelligence()
        
        # INTERFACE
        st.markdown(f"""
            <div class="main-card">
                <div style="font-size:0.7rem; color:#64748b; letter-spacing:3px;">{fonte} | AURAXIS V32 SOBERANO</div>
                <div class="price-hero">{p_final:.5f}</div>
                <div style="display:grid; grid-template-columns: 1fr 1fr 1fr; gap:10px; margin-top:15px;">
                    <div class="metric-box"><small>Z-SCORE</small><br><b>{m['z']:.2f}</b></div>
                    <div class="metric-box"><small>VOL. REL</small><br><b>{m['v']:.2f}x</b></div>
                    <div class="metric-box"><small>IA SCORE</small><br><b>{m['prob']:.1f}%</b></div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        

        # GATILHOS DE ENTRADA (Lógica Acumulada)
        st.write("")
        if m['v'] > 1.2:
            # Absorção de Fundo (Exaustão + Z-Score)
            if m['w_inf'] > abs(m['body']) * 1.5 and m['z'] < -2.0:
                st.markdown('<div class="signal-active" style="border-color:#3b82f6; background:#3b82f615; color:#3b82f6;">🛡️ ABSORÇÃO DE FUNDO: ALTA PROBABILIDADE DE REVERSÃO</div>', unsafe_allow_html=True)
            
            # Absorção de Topo
            if m['w_sup'] > abs(m['body']) * 1.5 and m['z'] > 2.0:
                st.markdown('<div class="signal-active" style="border-color:#3b82f6; background:#3b82f615; color:#3b82f6;">🛡️ ABSORÇÃO DE TOPO: ALTA PROBABILIDADE DE REVERSÃO</div>', unsafe_allow_html=True)

            # Impulso de IA (ML + Bayes)
            if m['prob'] > 78:
                st.markdown('<div class="signal-active" style="border-color:#10b981; background:#10b98115; color:#10b981;">🚀 CONFLUÊNCIA SOBERANA: IMPULSO DE COMPRA (IA+BAYES)</div>', unsafe_allow_html=True)
            elif m['prob'] < 22:
                st.markdown('<div class="signal-active" style="border-color:#ef4444; background:#ef444415; color:#ef4444;">🚀 CONFLUÊNCIA SOBERANA: IMPULSO DE VENDA (IA+BAYES)</div>', unsafe_allow_html=True)

        

except Exception as e:
    st.info("Recalibrando Motores Neurais...")

# Auto-Refresh (60s para respeitar limite da API gratuita)
st.markdown("""<meta http-equiv="refresh" content="60">""", unsafe_allow_html=True)
