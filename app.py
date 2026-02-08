import sqlite3
import pandas as pd
import streamlit as st
import urllib.parse
import plotly.express as px
from datetime import datetime, date, timedelta

# ==========================================
# DESIGN ZEN (SUAVE E RELAXANTE)
# ==========================================
st.set_page_config(page_title="Artmax Zen Business", layout="wide", page_icon="🌿")

def apply_ui():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Quicksand:wght@500;700&family=Nunito:wght@400;700&display=swap');
    
    .stApp { background-color: #F8F9FA; color: #4A4A4A; font-family: 'Nunito', sans-serif; }
    
    .header-box {
        background: linear-gradient(135deg, #E6E6FA, #F3E5F5);
        padding: 40px; border-radius: 0 0 30px 30px;
        border-bottom: 3px solid #D1C4E9; text-align: center; margin-bottom: 30px;
    }
    .main-title { font-family: 'Quicksand', sans-serif; font-size: 45px; color: #5E35B1; font-weight: 700; }
    
    /* FONTES GRANDES E SUAVES */
    label, p, .stMarkdown { font-size: 22px !important; color: #5D4037 !important; font-weight: 700 !important; }
    
    /* INPUTS LIMPOS */
    input, select, textarea, div[data-baseweb="select"] { 
        background-color: #FFFFFF !important; color: #2C3E50 !important; 
        font-size: 20px !important; border-radius: 12px !important; border: 1px solid #E0E0E0 !important;
    }

    .stButton>button {
        background: #9575CD !important; color: #FFFFFF !important;
        border-radius: 15px; height: 65px; font-size: 22px !important; font-weight: 700;
        border: none !important; transition: 0.3s;
    }
    .stButton>button:hover { background: #7E57C2 !important; transform: translateY(-2px); }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# BANCO DE DADOS
# ==========================================
def init_db():
    conn = sqlite3.connect("artmax_zen_v3.db", check_same_thread=False)
    conn.execute("CREATE TABLE IF NOT EXISTS agenda (id INTEGER PRIMARY KEY AUTOINCREMENT, data TEXT, hora TEXT, cliente TEXT, telefone TEXT, servico TEXT, profissional TEXT)")
    conn.execute("CREATE TABLE IF NOT EXISTS vendas (id INTEGER PRIMARY KEY AUTOINCREMENT, data TEXT, cliente TEXT, valor REAL, servico TEXT, profissional TEXT)")
    conn.execute("CREATE TABLE IF NOT EXISTS gastos (id INTEGER PRIMARY KEY AUTOINCREMENT, data TEXT, descricao TEXT, valor REAL)")
    conn.commit()
    return conn

db = init_db()

# ==========================================
# INTERFACE
# ==========================================
apply_ui()

if "auth" not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    st.markdown("<div class='header-box'><div class='main-title'>ARTMAX ZEN</div><p>Business Management</p></div>", unsafe_allow_html=True)
    u = st.text_input("Usuário")
    s = st.text_input("Senha", type="password")
    if st.button("Entrar no Sistema"):
        if u.lower() == "artmax" and s == "gesini123":
            st.session_state.auth = True
            st.rerun()
    st.stop()

menu = st.sidebar.radio("NAVEGAÇÃO", ["📅 Agenda", "🤖 Robô de Carinho", "💰 Caixa", "📉 Despesas", "📊 Relatórios & Comissão"])

# --- RELATÓRIOS COM COMISSÃO ---
if menu == "📊 Relatórios & Comissão":
    st.title("📊 Desempenho & Comissões")
    df_v = pd.read_sql("SELECT * FROM vendas", db)
    df_g = pd.read_sql("SELECT * FROM gastos", db)
    
    total_vendas = df_v['valor'].sum() if not df_v.empty else 0.0
    total_gastos = df_g['valor'].sum() if not df_g.empty else 0.0
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Faturamento", f"R$ {total_vendas:.2f}")
    col2.metric("Despesas", f"R$ {total_gastos:.2f}")
    col3.metric("Sobras", f"R$ {total_vendas - total_gastos:.2f}")

    st.divider()
    st.subheader("💰 Cálculo de Comissões (50%)")
    
    if df_v.empty:
        st.info("Aguardando as primeiras vendas para calcular as comissões. ✨")
    else:
        # Filtrando vendas apenas da Evelyn
        vendas_evelyn = df_v[df_v['profissional'] == 'Evelyn']['valor'].sum()
        comissao_evelyn = vendas_evelyn * 0.50
        
        c_ev1, c_ev2 = st.columns(2)
        c_ev1.write(f"**Total Evelyn:** R$ {vendas_evelyn:.2f}")
        c_ev2.warning(f"**Comissão Evelyn (50%): R$ {comissao_evelyn:.2f}**")

        st.plotly_chart(px.bar(df_v, x='profissional', y='valor', color='profissional', 
                               title="Produção por Profissional",
                               color_discrete_map={'Eunides': '#B39DDB', 'Evelyn': '#9575CD'}))

# --- GASTOS ---
elif menu == "📉 Despesas":
    st.title("📉 Registro de Gastos")
    with st.form("gastos"):
        desc = st.text_input("O que foi pago?")
        val = st.number_input("Valor R$", min_value=0.0)
        if st.form_submit_button("Registrar Saída"):
            db.execute("INSERT INTO gastos (data, descricao, valor) VALUES (?,?,?)", (date.today().isoformat(), desc, val))
            db.commit()
            st.success("Gasto registrado com sucesso!")
    
    st.divider()
    df_g_list = pd.read_sql("SELECT * FROM gastos ORDER BY id DESC", db)
    if df_g_list.empty:
        st.write("Nenhum gasto registrado este mês. Tudo sob controle! 🌿")
    else:
        st.dataframe(df_g_list[['data', 'descricao', 'valor']], use_container_width=True)

# (Outras abas como Agenda, Robô e Caixa seguem o mesmo padrão visual relaxante)