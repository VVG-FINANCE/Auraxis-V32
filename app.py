import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import requests
from sklearn.ensemble import RandomForestClassifier
from datetime import datetime

# --- 1. CONFIGURAÇÃO DE ALTA PERFORMANCE (Soberania V32) ---
st.set_page_config(page_title="AURAXIS V38 - OMNIS", layout="wide")
av_key = st.secrets.get("ALPHA_VANTAGE_KEY", "")

st.markdown("""
    <style>
    .stApp { background-color: #050505; color: #e2e8f0; }
    .main-card { background: #0d1117; border: 1px solid #30363d; padding: 25px; border-radius: 20px; text-align: center; }
    .price-hero { font-family: monospace; font-size: 4.2rem; font-weight: 700; color: #ffffff; margin: 0; }
    .metric-box { background: #161b22; padding: 10px; border-radius: 10px; border: 1px solid #30363d; }
    .signal-box { padding: 15px; border-radius: 12px; margin-top: 10px; font-weight: bold; border-left: 8px solid; }
    </style>
""", unsafe_allow_html=True)

# --- 2. CÁPSULA DE MEMÓRIA GERACIONAL (Injetada 26 Anos - V35) ---
MAPA_ESTRUTURAL = {
    "ZONAS": {"R3": 1.3950, "R2": 1.2540, "R1": 1.1520, "S1": 1.0820, "S2": 1.0450, "S3": 0.8225},
    "HIST_MAX": 1.6038, "HIST_MIN": 0.8225
}

# --- 3. GESTÃO DO DIÁRIO DE BORDO (Arquitetura V37) ---
if 'diario' not in st.session_state:
    st.session_state.diario = []

def registrar_no_diario(msg):
    agora = datetime.now().strftime('%H:%M')
    if not st.session_state.diario or msg != st.session_state.diario[0][8:]:
        st.session_state.diario.insert(0, f"[{agora}] {msg}")
        if len(st.session_state.diario) > 12: st.session_state.diario.pop()

# --- 4. MOTOR DE INTELIGÊNCIA INTEGRADO (V1 - V31) ---
class AuraxisEngine:
    def __init__(self, df):
        self.df = df
        self.last = df.iloc[-1]
        
    def process(self):
        # A. FÍSICA V1 (Anatomia de Candle)
        body = self.last['Close'] - self.last['Open']
        wick_inf = min(self.last['Open'], self.last['Close']) - self.last['Low']
        wick_sup = self.last['High'] - max(self.last['Open'], self.last['Close'])
        
        # B. ESTATÍSTICA V20 (Z-Score)
        m20 = self.df['Close'].rolling(20).mean().iloc[-1]
        s20 = self.df['Close'].rolling(20).std().iloc[-1]
        z = (self.last['Close'] - m20) / (s20 + 1e-9)
        
        # C. VOLUME V30 (Fluxo Institucional)
        v_rel = self.last['Volume'] / (self.df['Volume'].rolling(20).mean().iloc[-1] + 1e-9)
        
        # D. MACHINE LEARNING V31 (Random Forest c/ Bayes)
        self.df['B'] = self.df['Close'] - self.df['Open']
        self.df['V'] = self.df['Volume'] / (self.df['Volume'].rolling(20).mean() + 1e-9)
        self.df['Target'] = np.where(self.df['Close'].shift(-5) > self.df['Close'], 1, 0)
        train = self.df.dropna().tail(150)
        model = RandomForestClassifier(n_estimators=30).fit(train[['B', 'V']][:-5], train['Target'][:-5])
        prob_ml = model.predict_proba(train[['B', 'V']].iloc[[-1]])[0][1] * 100
        
        return {"z": z, "v": v_rel, "prob": prob_ml, "body": body, "w_inf": wick_inf, "w_sup": wick_sup}

# --- 5. REDUNDÂNCIA DUAL-CORE (V32) ---
def get_alpha_live(key):
    try:
        url = f'https://www.alphavantage.co/query?function=CURRENCY_EXCHANGE_RATE&from_currency=EUR&to_currency=USD&apikey={key}'
        return float(requests.get(url, timeout=3).json()['Realtime Currency Exchange Rate']['5. Exchange Rate'])
    except: return None

# --- 6. CICLO DE EXECUÇÃO OMNIS ---
try:
    data_1m = yf.download("EURUSD=X", period="1d", interval="1m", progress=False)
    
    if not data_1m.empty:
        # Preço Dual-Core (V32)
        p_live = get_alpha_live(api_key) if (api_key := st.sidebar.text_input("API Key", value=av_key, type="password")) else None
        p_final = p_live if p_live else data_1m['Close'].iloc[-1]
        
        # Processamento
        eng = AuraxisEngine(data_1m)
        m = eng.process()
        
        # MAPEAMENTO DE ESTRUTURA (V37)
        status_mapa = "EM EQUILÍBRIO"
        if p_final < MAPA_ESTRUTURAL['ZONAS']['S1']: status_mapa = "ZONA DE COMPRA GERACIONAL"
        if p_final > MAPA_ESTRUTURAL['ZONAS']['R1']: status_mapa = "ZONA DE VENDA GERACIONAL"

        # REGISTRO NO DIÁRIO DE BORDO
        if m['v'] > 1.8: registrar_no_diario(f"Pico de Volume Detectado em {p_final:.5f}")
        if m['prob'] > 85: registrar_no_diario("IA Score em nível de exaustão de alta.")
        
        # INTERFACE PRINCIPAL
        st.markdown(f"""
            <div class="main-card">
                <div style="color:#3b82f6; font-size:0.8rem; letter-spacing:2px;">AURAXIS V38 OMNIS</div>
                <div class="price-hero">{p_final:.5f}</div>
                <div style="color:#64748b; font-weight:bold; margin-bottom:15px;">{status_mapa}</div>
                <div style="display:grid; grid-template-columns: 1fr 1fr 1fr; gap:10px;">
                    <div class="metric-box"><small>IA SCORE</small><br><b style="font-size:1.3rem;">{m['prob']:.1f}%</b></div>
                    <div class="metric-box"><small>Z-SCORE</small><br><b style="font-size:1.3rem;">{m['z']:.2f}</b></div>
                    <div class="metric-box"><small>V-REL</small><br><b style="font-size:1.3rem;">{m['v']:.2f}x</b></div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        

        # GATILHOS DE CONFLUÊNCIA SOBERANA
        st.write("")
        if m['v'] > 1.2:
            if m['prob'] > 80 and p_final < MAPA_ESTRUTURAL['ZONAS']['S1']:
                st.markdown('<div class="signal-box" style="border-color:#10b981; background:#10b98115; color:#10b981;">🚀 CONFLUÊNCIA MESTRE: COMPRA INSTITUCIONAL (CICLO + IA)</div>', unsafe_allow_html=True)
            elif m['prob'] < 20 and p_final > MAPA_ESTRUTURAL['ZONAS']['R1']:
                st.markdown('<div class="signal-box" style="border-color:#ef4444; background:#ef444415; color:#ef4444;">🚀 CONFLUÊNCIA MESTRE: VENDA INSTITUCIONAL (CICLO + IA)</div>', unsafe_allow_html=True)
            
            # Absorção V1
            if m['w_inf'] > abs(m['body']) * 1.5 and m['z'] < -1.8:
                st.markdown('<div class="signal-box" style="border-color:#3b82f6; background:#3b82f615; color:#3b82f6;">🛡️ ABSORÇÃO DE FUNDO: PLAYERS DEFENDENDO POSIÇÃO</div>', unsafe_allow_html=True)

        # DIÁRIO DE BORDO (V37)
        st.markdown("### 📖 Diário de Bordo (Mapa de Estruturas)")
        for line in st.session_state.diario:
            st.markdown(f"> {line}")

except Exception as e:
    st.info("Sincronizando consciência omnis...")

st.markdown("""<meta http-equiv="refresh" content="60">""", unsafe_allow_html=True)
