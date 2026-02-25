import sqlite3
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
import urllib.parse
import plotly.express as px
from datetime import date, timedelta

# =========================
# (Opcional) Google Sheets
# =========================
try:
    import gspread
    from google.oauth2.service_account import Credentials
    HAS_SHEETS = True
except Exception:
    HAS_SHEETS = False

# =========================================================
# CONFIG
# =========================================================
APP_NAME = "Artmax Cabeleleiros"
DB_PATH = "artmax.db"

st.set_page_config(page_title=APP_NAME, layout="wide", page_icon="💜")

# =========================================================
# PALETA (roxo + dourado + preto + branco)
# =========================================================
C_BG = "#0B0B10"
C_TEXT = "rgba(255,255,255,0.92)"
C_MUTED = "rgba(255,255,255,0.70)"
C_SURFACE = "rgba(255,255,255,0.055)"
C_SURFACE_2 = "rgba(255,255,255,0.035)"

C_PURPLE_1 = "#4A00E0"
C_PURPLE_2 = "#8E2DE2"
C_GOLD = "#D4AF37"
C_GOLD_SOFT = "rgba(212,175,55,0.22)"
C_WHITE = "#FFFFFF"

PROFISSIONAIS = ["Eunides", "Evelyn"]
SERVICOS = ["Escova", "Progressiva", "Luzes", "Coloração", "Botox", "Relaxamento", "Sobrancelha", "Corte", "Outros"]

# =========================================================
# UI (premium + sidebar opaca + resizer)
# =========================================================
def apply_ui():
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=Inter:wght@400;500;600&display=swap');

    .stApp {{
        background: radial-gradient(circle at 20% 0%, rgba(142,45,226,0.30), rgba(11,11,16,0.92) 40%),
                  radial-gradient(circle at 80% 30%, rgba(212,175,55,0.12), rgba(11,11,16,0.0) 45%), {C_BG};
        color: {C_TEXT};
        font-family: 'Inter', sans-serif;
    }}

    .app-header {{
        background: linear-gradient(135deg, rgba(74,0,224,0.60), rgba(142,45,226,0.35));
        border: 1px solid {C_GOLD_SOFT};
        padding: 18px 22px;
        border-radius: 20px;
        margin-bottom: 16px;
        box-shadow: 0 16px 40px rgba(0,0,0,0.45);
    }}
    .app-title {{
        font-family: 'Playfair Display', serif;
        font-size: 28px;
        font-weight: 700;
        color: {C_WHITE};
    }}

    div[data-testid="stForm"], div[data-testid="stExpander"], div[data-testid="stMetric"] {{
        background: {C_SURFACE} !important;
        border: 1px solid {C_GOLD_SOFT} !important;
        border-radius: 20px !important;
        padding: 18px !important;
    }}

    input, textarea, div[data-baseweb="select"] {{
        background-color: rgba(255,255,255,0.92) !important;
        color: #101018 !important;
        border-radius: 14px !important;
    }}

    .stButton>button {{
        background: linear-gradient(90deg, {C_GOLD}, #B8860B) !important;
        color: #0B0B10 !important;
        border-radius: 14px;
        height: 48px;
        font-weight: 800;
    }}
    </style>
    """, unsafe_allow_html=True)

def header():
    st.markdown(f'<div class="app-header"><div class="app-title">{APP_NAME}</div></div>', unsafe_allow_html=True)

# =========================================================
# DB & COMISSÃO
# =========================================================
COMISSAO_EVELYN = {"Escova": 0.50, "Progressiva": 0.50, "Botox": 0.50, "Sobrancelha": 0.60, "Coloração": 0.40, "Relaxamento": 0.50}

def calc_comissao(prof, serv, valor):
    if prof.strip().lower() != "evelyn": return 0.0
    return float(valor) * COMISSAO_EVELYN.get(serv, 0.50)

def init_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.execute("CREATE TABLE IF NOT EXISTS agenda (id INTEGER PRIMARY KEY AUTOINCREMENT, data TEXT, hora TEXT, cliente TEXT, telefone TEXT, servico TEXT, profissional TEXT)")
    conn.execute("CREATE TABLE IF NOT EXISTS vendas (id INTEGER PRIMARY KEY AUTOINCREMENT, data TEXT, cliente TEXT, valor REAL, servico TEXT, profissional TEXT, comissao REAL DEFAULT 0)")
    conn.execute("CREATE TABLE IF NOT EXISTS gastos (id INTEGER PRIMARY KEY AUTOINCREMENT, data TEXT, descricao TEXT, valor REAL)")
    conn.commit()
    return conn

db = init_db()

# =========================================================
# WHATSAPP
# =========================================================
def build_whatsapp_link(nome, tel, servico, hora="", tipo="confirmacao"):
    if not tel: return None
    msg = f"Olá {nome}! ✨ Confirmamos seu horário para {servico} às {hora}."
    tel_limpo = "".join(filter(str.isdigit, tel))
    return f"https://wa.me/55{tel_limpo}?text={urllib.parse.quote(msg)}"

def open_whatsapp(link):
    if link: components.html(f"<script>window.open('{link}', '_blank');</script>", height=0)

# =========================================================
# APP LOGIC
# =========================================================
apply_ui()

if "auth" not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    u = st.text_input("Usuário")
    s = st.text_input("Senha", type="password")
    if st.button("Entrar"):
        if u == "artmax" and s == "gesini123":
            st.session_state.auth = True
            st.rerun()
    st.stop()

header()
menu = st.sidebar.radio("Menu", ["Agenda", "Checkout", "Relatórios"])

# --- ABA AGENDA ---
if menu == "Agenda":
    st.subheader("Novo agendamento")
    
    # ✅ CORREÇÃO: Fora do form para reatividade
    serv_base = st.selectbox("Procedimento", SERVICOS, key="ag_main")
    outro_serv = ""
    if serv_base == "Outros":
        outro_serv = st.text_input("Especifique o serviço", placeholder="Ex: Hidratação")

    with st.form("ag_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        cli, tel = c1.text_input("Cliente"), c2.text_input("WhatsApp")
        prof = st.selectbox("Profissional", PROFISSIONAIS)
        dt, hr = st.date_input("Data"), st.time_input("Horário")
        
        if st.form_submit_button("Confirmar Agendamento"):
            serv_f = outro_serv if serv_base == "Outros" else serv_base
            db.execute("INSERT INTO agenda (data, hora, cliente, telefone, servico, profissional) VALUES (?,?,?,?,?,?)",
                       (dt.isoformat(), hr.strftime("%H:%M"), cli, tel, serv_f, prof))
            db.commit()
            open_whatsapp(build_whatsapp_link(cli, tel, serv_f, hr.strftime("%H:%M")))
            st.success("Agendado!")

# --- ABA CHECKOUT ---
elif menu == "Checkout":
    st.subheader("Finalizar atendimento")
    
    # ✅ CORREÇÃO: Fora do form
    v_serv_base = st.selectbox("Procedimento", SERVICOS, key="chk_main")
    v_outro_serv = ""
    if v_serv_base == "Outros":
        v_outro_serv = st.text_input("Qual o serviço realizado?", key="chk_outro")

    with st.form("caixa", clear_on_submit=True):
        v_cli = st.text_input("Cliente")
        v_val = st.number_input("Valor (R$)", min_value=0.0)
        v_prof = st.selectbox("Profissional", PROFISSIONAIS)
        
        if st.form_submit_button("Concluir"):
            serv_f = v_outro_serv if v_serv_base == "Outros" else v_serv_base
            comis = calc_comissao(v_prof, serv_f, v_val)
            db.execute("INSERT INTO vendas (data, cliente, valor, servico, profissional, comissao) VALUES (?,?,?,?,?,?)",
                       (date.today().isoformat(), v_cli, v_val, serv_f, v_prof, comis))
            db.commit()
            st.success(f"Venda salva! Comissão Evelyn: R$ {comis:.2f}")

# --- ABA RELATÓRIOS ---
elif menu == "Relatórios":
    df = pd.read_sql("SELECT * FROM vendas", db)
    st.dataframe(df, use_container_width=True)