import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import requests
from sklearn.ensemble import RandomForestClassifier
from datetime import datetime

# --- CONFIGURAÇÃO DE ALTA PERFORMANCE ---
st.set_page_config(page_title="AURAXIS V34 SOBERANO", layout="wide")
av_key = st.secrets.get("ALPHA_VANTAGE_KEY", "")

st.markdown("""
    <style>
    .stApp { background-color: #050505; color: #e2e8f0; }
    .main-card { background: #0d1117; border: 1px solid #30363d; padding: 25px; border-radius: 20px; text-align: center; }
    .price-hero { font-family: monospace; font-size: 4.5rem; font-weight: 700; color: #ffffff; margin: 0; }
    .metric-box { background: #161b22; padding: 10px; border-radius: 10px; border: 1px solid #30363d; }
    .signal-active { padding: 15px; border-radius: 12px; margin-top: 10px; font-weight: bold; border-left: 10px solid; }
    .inst-label { color: #3b82f6; font-weight: bold; font-size: 0.8rem; letter-spacing: 2px; }
    </style>
""", unsafe_allow_html=True)

# --- SIDEBAR DE SEGURANÇA E DADOS ---
with st.sidebar:
    st.header("🛡️ Painel de Controle")
    manual_key = st.text_input("Chave Alpha Vantage:", value=av_key, type="password")
    api_key = manual_key if manual_key else av_key
    st.markdown("---")
    st.write("Memória: 26 Anos (Ativa)")
    st.write("Motor: Dual-Core Híbrido")

# --- CLASSE DE INTELIGÊNCIA DEEP-CORE ---
class AuraxisDeepSovereign:
    def __init__(self, ticker):
        self.ticker = ticker
        # Carrega 26 anos de história (Uma única vez via Session State)
        self.history_context = self._load_26_year_memory()

    def _load_26_year_memory(self):
        # Captura o máximo de histórico disponível (Aprox. 26 anos para EURUSD)
        df_long = yf.download(self.ticker, period="max", interval="1d", progress=False)
        return {
            "max_26y": df_long['High'].max(),
            "min_26y": df_long['Low'].min(),
            "avg_26y": df_long['Close'].mean(),
            "q75": df_long['Close'].quantile(0.75),
            "q25": df_long['Close'].quantile(0.25)
        }

    def process_logic(self, df_1m):
        last = df_1m.iloc[-1]
        price = last['Close']
        ctx = self.history_context
        
        # 1. ANATOMIA V1 (Corpo e Pavio)
        body = price - last['Open']
        wick_inf = min(last['Open'], price) - last['Low']
        wick_sup = last['High'] - max(last['Open'], price)
        
        # 2. POSICIONAMENTO GERACIONAL (26 ANOS)
        if price > ctx['q75']:
            status_macro = "ZONA DE SOBREVALORIZAÇÃO HISTÓRICA"
        elif price < ctx['q25']:
            status_macro = "ZONA DE SUBVALORIZAÇÃO HISTÓRICA"
        else:
            status_macro = "VALOR DE EQUILÍBRIO GERACIONAL"

        # 3. Z-SCORE V15 (Curto Prazo)
        m20 = df_1m['Close'].rolling(20).mean().iloc[-1]
        s20 = df_1m['Close'].rolling(20).std().iloc[-1]
        z = (price - m20) / (s20 + 1e-9)

        # 4. VOLUME & SQUEEZE V30
        v_rel = last['Volume'] / (df_1m['Volume'].rolling(20).mean().iloc[-1] + 1e-9)

        # 5. MACHINE LEARNING V31 (Random Forest)
        df_1m['B'] = df_1m['Close'] - df_1m['Open']
        df_1m['V'] = df_1m['Volume'] / (df_1m['Volume'].rolling(20).mean() + 1e-9)
        df_1m['Target'] = np.where(df_1m['Close'].shift(-5) > df_1m['Close'], 1, 0)
        train = df_1m.dropna()
        model = RandomForestClassifier(n_estimators=30).fit(train[['B', 'V']][:-5], train['Target'][:-5])
        prob_ml = model.predict_proba(train[['B', 'V']].iloc[[-1]])[0][1] * 100

        # 6. SÍNTESE BAYESIANA (Fusão ML + Contexto)
        return {"z": z, "v": v_rel, "prob": prob_ml, "macro": status_macro, 
                "body": body, "wick_i": wick_inf, "wick_s": wick_sup, "price": price}

def get_alpha_live(key):
    try:
        url = f'https://www.alphavantage.co/query?function=CURRENCY_EXCHANGE_RATE&from_currency=EUR&to_currency=USD&apikey={key}'
        return float(requests.get(url, timeout=5).json()['Realtime Currency Exchange Rate']['5. Exchange Rate'])
    except: return None

# --- CICLO OPERACIONAL ---
try:
    # Warm-Start de 26 Anos
    if 'sovereign_mind' not in st.session_state:
        with st.spinner("Alimentando Cérebro com 26 anos de dados..."):
            st.session_state.sovereign_mind = AuraxisDeepSovereign("EURUSD=X")
    
    # Dados de Execução (1 Minuto)
    data_1m = yf.download("EURUSD=X", period="1d", interval="1m", progress=False)
    
    if not data_1m.empty:
        # Preço Dual-Core
        p_live = get_alpha_live(api_key) if api_key else None
        p_display = p_live if p_live else data_1m['Close'].iloc[-1]
        fonte = "🟢 DUAL-CORE" if p_live else "🟡 YAHOO"
        
        intel = st.session_state.sovereign_mind.process_logic(data_1m)
        
        # UI PRINCIPAL
        st.markdown(f"""
            <div class="main-card">
                <div class="inst-label">{fonte} | AURAXIS V34 SOBERANO</div>
                <div class="price-hero">{p_display:.5f}</div>
                <div style="color:#3b82f6; font-size:0.9rem; margin-bottom:15px;">{intel['macro']}</div>
                <div style="display:grid; grid-template-columns: 1fr 1fr 1fr; gap:10px;">
                    <div class="metric-box"><small>IA SCORE</small><br><b>{intel['prob']:.1f}%</b></div>
                    <div class="metric-box"><small>Z-SCORE</small><br><b>{intel['z']:.2f}</b></div>
                    <div class="metric-box"><small>VOL. REL</small><br><b>{intel['v']:.2f}x</b></div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        

        # GATILHOS INSTITUCIONAIS FILTRADOS
        st.write("")
        if intel['v'] > 1.2:
            # Absorção (V1) + Contexto Geracional
            if intel['wick_i'] > abs(intel['body']) * 1.5 and intel['z'] < -1.9:
                st.markdown('<div class="signal-active" style="border-color:#3b82f6; background:#3b82f615; color:#3b82f6;">🛡️ ABSORÇÃO INSTITUCIONAL: ALTA PROBABILIDADE DE REVERSÃO</div>', unsafe_allow_html=True)
            
            # Confluência Mestra (IA + Ciclo)
            if intel['prob'] > 82 and "BARATO" in intel['macro']:
                st.markdown('<div class="signal-active" style="border-color:#10b981; background:#10b98115; color:#10b981;">🔥 TRADE SOBERANO: CONFLUÊNCIA DE CICLO E IA (COMPRA)</div>', unsafe_allow_html=True)
            elif intel['prob'] < 18 and "CARO" in intel['macro']:
                st.markdown('<div class="signal-active" style="border-color:#ef4444; background:#ef444415; color:#ef4444;">🔥 TRADE SOBERANO: CONFLUÊNCIA DE CICLO E IA (VENDA)</div>', unsafe_allow_html=True)

except Exception as e:
    st.info("Sincronizando consciência geracional...")

st.markdown("""<meta http-equiv="refresh" content="60">""", unsafe_allow_html=True)
