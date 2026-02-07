import sqlite3
import pandas as pd
import streamlit as st
import urllib.parse
import plotly.express as px
from datetime import datetime, date, timedelta

# ==========================================
# DESIGN LUXO (PRETO, ROXO E DOURADO)
# ==========================================
st.set_page_config(page_title="Artmax Exclusive VIP", layout="wide", page_icon="👑")

COLOR_PURPLE = "#6A0DAD" 
COLOR_GOLD = "#FFD700"   
COLOR_BG = "#000000"     

def apply_ui():
    st.markdown(f"""
    <style>
    .stApp {{ background-color: {COLOR_BG}; color: #FFFFFF; }}
    .logo-header {{
        background: linear-gradient(90deg, #1a0033, {COLOR_PURPLE}, #1a0033);
        padding: 30px; border-radius: 0 0 30px 30px;
        border-bottom: 4px solid {COLOR_GOLD}; text-align: center; margin-bottom: 20px;
    }}
    .logo-main {{ font-family: 'serif'; font-size: 50px; color: {COLOR_GOLD}; font-weight: bold; letter-spacing: 5px; }}
    
    /* Campos brancos com letra preta para leitura total */
    input, select, textarea, div[data-baseweb="select"], .stDateInput div {{ 
        background-color: #FFFFFF !important; 
        color: #000000 !important; 
        font-size: 18px !important; 
        font-weight: bold !important;
    }}
    
    label, p, span {{ font-size: 20px !important; color: #FFFFFF !important; font-weight: bold !important; }}
    
    .stButton>button {{
        width: 100%; border-radius: 12px; height: 60px;
        background: {COLOR_PURPLE} !important; color: #FFFFFF !important;
        border: 2px solid {COLOR_GOLD} !important; font-size: 20px !important; font-weight: bold;
    }}
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# BANCO DE DADOS
# ==========================================
def init_db():
    conn = sqlite3.connect("artmax_final_v11.db", check_same_thread=False)
    conn.execute("""CREATE TABLE IF NOT EXISTS agenda (
        id INTEGER PRIMARY KEY AUTOINCREMENT, data TEXT, hora TEXT, 
        cliente TEXT, telefone TEXT, servico TEXT, profissional TEXT)""")
    conn.execute("""CREATE TABLE IF NOT EXISTS vendas (
        id INTEGER PRIMARY KEY AUTOINCREMENT, data TEXT, cliente TEXT, 
        valor REAL, servico TEXT, profissional TEXT)""")
    conn.execute("""CREATE TABLE IF NOT EXISTS gastos (
        id INTEGER PRIMARY KEY AUTOINCREMENT, data TEXT, descricao TEXT, valor REAL)""")
    conn.commit()
    return conn

db = init_db()

def disparar_whatsapp(nome, tel, servico, hora, tipo="confirmacao"):
    if tipo == "confirmacao":
        msg = f"Olá {nome}! ✨ Seu agendamento de {servico} na ARTMAX às {hora} foi confirmado. Já estamos te esperando! 💇‍♀️"
    elif tipo == "lembrete":
        msg = f"Olá {nome}! 🚨 Lembrete ARTMAX: seu atendimento de {servico} começa em 2 horas ({hora})."
    else:
        msg = f"Olá {nome}! ✨ Atendimento de {servico} finalizado com sucesso. A ARTMAX agradece a preferência! 💜"
    
    tel_limpo = "".join(filter(str.isdigit, tel))
    link = f"https://wa.me/55{tel_limpo}?text={urllib.parse.quote(msg)}"
    js = f"window.open('{link}', '_blank').focus();"
    st.components.v1.html(f"<script>{js}</script>", height=0)

# ==========================================
# INTERFACE
# ==========================================
apply_ui()

if "auth" not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    st.markdown("<div class='logo-header'><div class='logo-main'>ARTMAX VIP</div></div>", unsafe_allow_html=True)
    u = st.text_input("Login")
    s = st.text_input("Senha", type="password")
    if st.button("ACESSAR SISTEMA"):
        if u == "artmax" and s == "gesini123":
            st.session_state.auth = True
            st.rerun()
    st.stop()

menu = st.sidebar.radio("MENU", ["📅 Agenda", "🤖 Robô", "💰 Caixa", "📉 Gastos", "📊 Lucros"])

# --- ABA 1: AGENDA ---
if menu == "📅 Agenda":
    st.title("Marcar Atendimento")
    with st.form("ag", clear_on_submit=True):
        c1, c2 = st.columns(2)
        cli = c1.text_input("Nome Cliente")
        tel = c2.text_input("WhatsApp")
        serv = st.selectbox("Serviço", ["Escova", "Progressiva", "Luzes", "Coloração", "Botox", "Corte", "Outros"])
        prof = st.selectbox("Profissional", ["Eunides", "Evelyn"])
        c3, c4 = st.columns(2)
        dt = c3.date_input("Data", date.today())
        hr = c4.time_input("Hora")
        if st.form_submit_button("SALVAR E NOTIFICAR"):
            db.execute("INSERT INTO agenda (data, hora, cliente, telefone, servico, profissional) VALUES (?,?,?,?,?,?)",
                       (dt.isoformat(), hr.strftime("%H:%M"), cli, tel, serv, prof))
            db.commit()
            disparar_whatsapp(cli, tel, serv, hr.strftime("%H:%M"), "confirmacao")

# --- ABA 2: ROBÔ ---
elif menu == "🤖 Robô":
    st.title("🤖 Robô Artmax")
    hoje = date.today().isoformat()
    df_hoje = pd.read_sql("SELECT * FROM agenda WHERE data = ?", db, params=[hoje])
    for _, r in df_hoje.iterrows():
        horario = datetime.strptime(f"{hoje} {r['hora']}", "%Y-%m-%d %H:%M")
        if timedelta(hours=1) < (horario - datetime.now()) <= timedelta(hours=2.5):
            st.warning(f"🚨 DISPARANDO AVISO: {r['cliente']}")
            if st.button(f"MANDAR MENSAGEM: {r['cliente']}"):
                disparar_whatsapp(r['cliente'], r['telefone'], r['servico'], r['hora'], "lembrete")
        else:
            st.write(f"✅ {r['cliente']} - {r['hora']} (Aguardando prazo)")

# --- ABA 3: CAIXA ---
elif menu == "💰 Caixa":
    st.title("Finalizar Atendimento")
    with st.form("venda"):
        v_cli = st.text_input("Cliente")
        v_tel = st.text_input("WhatsApp")
        v_serv = st.selectbox("Serviço", ["Escova", "Progressiva", "Luzes", "Coloração", "Botox", "Corte", "Outros"])
        v_prof = st.selectbox("Profissional", ["Eunides", "Evelyn"])
        v_valor = st.number_input("Valor (R$)", min_value=0.0)
        if st.form_submit_button("CONCLUIR E AGRADECER"):
            db.execute("INSERT INTO vendas (data, cliente, valor, servico, profissional) VALUES (?,?,?,?,?)",
                       (date.today().isoformat(), v_cli, v_valor, v_serv, v_prof))
            db.commit()
            disparar_whatsapp(v_cli, v_tel, v_serv, "", "agradecimento")

# --- ABA 4: GASTOS ---
elif menu == "📉 Gastos":
    st.title("📉 Registrar Despesas")
    with st.form("gastos"):
        desc = st.text_input("Descrição (Ex: Produtos, Luz, Aluguel)")
        val_g = st.number_input("Valor do Gasto (R$)", min_value=0.0)
        if st.form_submit_button("SALVAR GASTO"):
            db.execute("INSERT INTO gastos (data, descricao, valor) VALUES (?,?,?)",
                       (date.today().isoformat(), desc, val_g))
            db.commit()
            st.success("Gasto registrado!")

# --- ABA 5: LUCROS ---
elif menu == "📊 Lucros":
    st.title("Resultados Financeiros")
    df_v = pd.read_sql("SELECT * FROM vendas", db)
    df_g = pd.read_sql("SELECT * FROM gastos", db)
    
    receita = df_v['valor'].sum() if not df_v.empty else 0
    despesa = df_g['valor'].sum() if not df_g.empty else 0
    
    c1, c2, c3 = st.columns(3)
    c1.metric("ENTRADA TOTAL", f"R$ {receita:,.2f}")
    c2.metric("SAÍDA TOTAL", f"R$ {despesa:,.2f}")
    c3.metric("LUCRO LÍQUIDO", f"R$ {receita - despesa:,.2f}")
    
    if not df_v.empty:
        fig = px.bar(df_v, x="profissional", y="valor", color="profissional", barmode="group",
                     color_discrete_map={"Eunides": COLOR_GOLD, "Evelyn": COLOR_PURPLE})
        st.plotly_chart(fig, use_container_width=True)