import sqlite3
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
import urllib.parse
import plotly.express as px
from datetime import date, datetime, timedelta
from pathlib import Path

# =========================================================
# CONFIG
# =========================================================
APP_NAME = "Artmax Cabeleleiros"
DB_PATH = "artmax.db"
LOGO_PATH = "logo.png"

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
SERVICOS = ["Escova", "Progressiva", "Luzes", "Coloração", "Botox", "Corte", "Outros"]

# =========================================================
# UI (feminina / premium + glow)
# =========================================================
def apply_ui():
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=Inter:wght@400;500;600&display=swap');

    .stApp {{
        background:
          radial-gradient(circle at 20% 0%, rgba(142,45,226,0.30), rgba(11,11,16,0.92) 40%),
          radial-gradient(circle at 80% 30%, rgba(212,175,55,0.12), rgba(11,11,16,0.0) 45%),
          {C_BG};
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

    .app-sub {{
        font-size: 13px;
        color: {C_MUTED};
        margin-top: 6px;
    }}

    .gold-dot {{
        display: inline-block;
        width: 9px;
        height: 9px;
        background: {C_GOLD};
        border-radius: 50%;
        margin-right: 10px;
        box-shadow: 0 0 18px rgba(212,175,55,0.40);
    }}

    div[data-testid="stForm"], div[data-testid="stExpander"], div[data-testid="stMetric"] {{
        background: {C_SURFACE} !important;
        border: 1px solid {C_GOLD_SOFT} !important;
        border-radius: 20px !important;
        padding: 18px !important;
    }}

    div[data-testid="stDataFrame"] {{
        background: {C_SURFACE_2} !important;
        border-radius: 18px !important;
    }}

    div[data-testid="stMetric"] * {{
        color: {C_TEXT} !important;
        opacity: 1 !important;
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
        box-shadow: 0 10px 26px rgba(212,175,55,0.16);
    }}

    .stButton>button:hover {{
        box-shadow: 0 14px 34px rgba(212,175,55,0.22),
                    0 0 24px rgba(142,45,226,0.20);
    }}

    section[data-testid="stSidebar"] {{
        background: linear-gradient(180deg, rgba(74,0,224,0.22), rgba(11,11,16,0.96)) !important;
    }}

    section[data-testid="stSidebar"] * {{
        color: {C_TEXT} !important;
    }}

    .login-wrap {{
        display: flex;
        justify-content: center;
        align-items: center;
        padding-top: 40px;
    }}

    .login-card {{
        width: 460px;
        background: {C_SURFACE};
        border: 1px solid {C_GOLD_SOFT};
        border-radius: 22px;
        padding: 24px;
        box-shadow: 0 22px 60px rgba(0,0,0,0.55);
    }}

    .login-title {{
        font-family: 'Playfair Display', serif;
        font-size: 26px;
        font-weight: 700;
        color: {C_WHITE};
        margin-bottom: 6px;
    }}

    .login-sub {{
        color: {C_MUTED};
        font-size: 13px;
        margin-bottom: 14px;
    }}
    </style>
    """, unsafe_allow_html=True)

def header():
    st.markdown(
        f"""
        <div class="app-header">
            <div class="app-title"><span class="gold-dot"></span>{APP_NAME}</div>
            <div class="app-sub">Agenda • Atendimento • Financeiro • Relatórios</div>
        </div>
        """,
        unsafe_allow_html=True
    )

def logo_exists():
    return Path(LOGO_PATH).exists()

# =========================================================
# REGRA
# =========================================================
def calc_comissao(profissional, valor):
    return float(valor) if profissional == "Evelyn" else 0.0

def month_range(year, month):
    start = date(year, month, 1)
    end = date(year + (month // 12), (month % 12) + 1, 1)
    return start, end

# =========================================================
# DB
# =========================================================
def init_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.execute("""CREATE TABLE IF NOT EXISTS agenda (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        data TEXT, hora TEXT, cliente TEXT,
        telefone TEXT, servico TEXT, profissional TEXT
    )""")
    conn.execute("""CREATE TABLE IF NOT EXISTS vendas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        data TEXT, cliente TEXT, valor REAL,
        servico TEXT, profissional TEXT, comissao REAL
    )""")
    conn.execute("""CREATE TABLE IF NOT EXISTS gastos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        data TEXT, descricao TEXT, valor REAL
    )""")
    conn.commit()
    return conn

db = init_db()

# =========================================================
# APP
# =========================================================
apply_ui()

if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.markdown("<style>section[data-testid='stSidebar']{display:none}</style>", unsafe_allow_html=True)
    st.markdown("<div class='login-wrap'><div class='login-card'>", unsafe_allow_html=True)

    if logo_exists():
        st.image(LOGO_PATH, use_container_width=True)

    st.markdown(f"<div class='login-title'>{APP_NAME}</div>", unsafe_allow_html=True)
    st.markdown("<div class='login-sub'>Acesso restrito ao sistema.</div>", unsafe_allow_html=True)

    u = st.text_input("Usuário")
    s = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        if u.lower() == "artmax" and s == "gesini123":
            st.session_state.auth = True
            st.rerun()
        else:
            st.error("Usuário ou senha inválidos.")

    st.markdown("</div></div>", unsafe_allow_html=True)
    st.stop()

header()

if logo_exists():
    st.sidebar.image(LOGO_PATH, use_container_width=True)

year = st.sidebar.selectbox("Ano", [2024, 2025, 2026], index=1)
month = st.sidebar.selectbox("Mês", list(range(1, 13)), index=date.today().month - 1)
start_m, end_m = month_range(year, month)

menu = st.sidebar.radio("Menu", ["Agenda", "Checkout", "Despesas", "Relatórios"])

# (restante do código permanece exatamente igual)
