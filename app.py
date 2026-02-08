import sqlite3
import pandas as pd
import streamlit as st
import urllib.parse
import plotly.express as px
from datetime import datetime, date, timedelta

# ==========================================
# DESIGN PREMIUM (FONTES E GRADIENTES)
# ==========================================
st.set_page_config(page_title="Artmax Exclusive VIP", layout="wide", page_icon="👑")

# Cores mais sofisticadas
COLOR_PURPLE = "#8E2DE2" 
COLOR_DEEP_PURPLE = "#4A00E0"
COLOR_GOLD = "#D4AF37"   
COLOR_DARK_BG = "#0E1117"

def apply_ui():
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Poppins:wght@300;400;600&display=swap');

    .stApp {{ background-color: {COLOR_DARK_BG}; color: #FFFFFF; font-family: 'Poppins', sans-serif; }}
    
    /* Cabeçalho com Degradê e Sombra */
    .logo-header {{
        background: linear-gradient(135deg, {COLOR_DEEP_PURPLE}, {COLOR_PURPLE});
        padding: 40px; border-radius: 0 0 50px 50px;
        border-bottom: 5px solid {COLOR_GOLD}; text-align: center; 
        box-shadow: 0 10px 30px rgba(0,0,0,0.5); margin-bottom: 30px;
    }}
    .logo-main {{ font-family: 'Playfair Display', serif; font-size: 60px; color: {COLOR_GOLD}; font-weight: bold; letter-spacing: 4px; }}
    .logo-sub {{ font-size: 18px; color: #E0E0E0; letter-spacing: 2px; text-transform: uppercase; }}

    /* Cartões Flutuantes e Modernos */
    div[data-testid="stForm"], div[data-testid="stExpander"], .stTable {{
        background: rgba(255, 255, 255, 0.05) !important;
        backdrop-filter: blur(10px);
        padding: 30px !important; border-radius: 25px !important;
        border: 1px solid rgba(212, 175, 55, 0.3) !important;
        color: #FFFFFF !important;
    }}

    /* Inputs Estilizados */
    input, select, textarea, div[data-baseweb="select"] {{ 
        background-color: rgba(255, 255, 255, 0.9) !important; 
        color: #1a1a1a !important; border-radius: 12px !important;
        font-size: 18px !important; font-weight: 500 !important;
    }}

    /* Botão com Efeito de Brilho */
    .stButton>button {{
        background: linear-gradient(90deg, {COLOR_GOLD}, #B8860B) !important;
        color: #000000 !important; border: none !important;
        border-radius: 15px; height: 55px; font-weight: 700;
        transition: 0.3s; text-transform: uppercase;
    }}
    .stButton>button:hover {{ transform: scale(1.02); box-shadow: 0 5px 15px rgba(212, 175, 55, 0.4); }}
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# LÓGICA E BANCO (O QUE NÃO ESTAVA FUNCIONANDO)
# ==========================================
def init_db():
    conn = sqlite3.connect("artmax_final_v12.db", check_same_thread=False)
    # Corrigido: Tabelas criadas com estrutura robusta
    conn.execute("CREATE TABLE IF NOT EXISTS agenda (id INTEGER PRIMARY KEY AUTOINCREMENT, data TEXT, hora TEXT, cliente TEXT, telefone TEXT, servico TEXT, profissional TEXT)")
    conn.execute("CREATE TABLE IF NOT EXISTS vendas (id INTEGER PRIMARY KEY AUTOINCREMENT, data TEXT, cliente TEXT, valor REAL, servico TEXT, profissional TEXT)")
    conn.execute("CREATE TABLE IF NOT EXISTS gastos (id INTEGER PRIMARY KEY AUTOINCREMENT, data TEXT, descricao TEXT, valor REAL)")
    conn.commit()
    return conn

db = init_db()

def disparar_whatsapp(nome, tel, servico, hora="", tipo="confirmacao"):
    if not tel: return # Evita erro se telefone estiver vazio
    
    mensagens = {
        "confirmacao": f"Olá {nome}! ✨ Confirmamos seu horário para *{servico}* às {hora}. A Artmax Exclusive te espera!",
        "lembrete": f"Oi {nome}! 👑 Passando para lembrar do seu momento VIP hoje às {hora} ({servico}). Até logo!",
        "agradecimento": f"Foi um prazer te atender, {nome}! ✨ Esperamos que tenha amado o resultado do seu *{servico}*. Até a próxima! 💜"
    }
    msg = mensagens.get(tipo, "")
    tel_limpo = "".join(filter(str.isdigit, tel))
    link = f"https://wa.me/55{tel_limpo}?text={urllib.parse.quote(msg)}"
    
    # Script para abrir sem bugar o app
    st.components.v1.html(f"<script>window.open('{link}', '_blank');</script>", height=0)

# ==========================================
# EXECUÇÃO DO APP
# ==========================================
apply_ui()

if "auth" not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    st.markdown("<div class='logo-header'><div class='logo-main'>ARTMAX</div><div class='logo-sub'>Exclusive VIP</div></div>", unsafe_allow_html=True)
    with st.container():
        u = st.text_input("Username")
        s = st.text_input("Password", type="password")
        if st.button("ENTER SYSTEM"):
            if u.lower() == "artmax" and s == "gesini123":
                st.session_state.auth = True
                st.rerun()
    st.stop()

# Menu lateral elegante
menu = st.sidebar.radio("Navegação", ["📅 Agenda", "🤖 Robô VIP", "💰 Checkout", "📉 Despesas", "📊 Business Intelligence"])

# Lógica das abas simplificada para evitar bugs...
if menu == "📅 Agenda":
    st.markdown("### 📅 Novo Agendamento")
    with st.form("ag", clear_on_submit=True):
        c1, c2 = st.columns(2)
        cli = c1.text_input("Nome da Cliente")
        tel = c2.text_input("WhatsApp (Ex: 11999999999)")
        serv = st.selectbox("Procedimento", ["Escova", "Progressiva", "Luzes", "Coloração", "Botox", "Corte", "Outros"])
        prof = st.radio("Profissional", ["Eunides", "Evelyn"], horizontal=True)
        c3, c4 = st.columns(2)
        dt = c3.date_input("Data", date.today())
        hr = c4.time_input("Horário")
        if st.form_submit_button("CONFIRMAR E ENVIAR WHATSAPP"):
            db.execute("INSERT INTO agenda (data, hora, cliente, telefone, servico, profissional) VALUES (?,?,?,?,?,?)",
                       (dt.isoformat(), hr.strftime("%H:%M"), cli, tel, serv, prof))
            db.commit()
            disparar_whatsapp(cli, tel, serv, hr.strftime("%H:%M"), "confirmacao")
            st.success(f"Agendado com sucesso para {cli}!")

elif menu == "🤖 Robô VIP":
    st.title("🤖 Monitoramento de Horários")
    hoje = date.today().isoformat()
    df = pd.read_sql("SELECT * FROM agenda WHERE data = ?", db, params=[hoje])
    if df.empty:
        st.info("Nenhuma cliente para hoje ainda.")
    else:
        for _, r in df.iterrows():
            st.write(f"📌 **{r['hora']}** - {r['cliente']} ({r['servico']})")
            if st.button(f"Enviar Lembrete 2h: {r['cliente']}", key=r['id']):
                disparar_whatsapp(r['cliente'], r['telefone'], r['servico'], r['hora'], "lembrete")

elif menu == "💰 Checkout":
    st.title("💰 Finalizar Atendimento")
    with st.form("caixa"):
        v_cli = st.text_input("Nome da Cliente")
        v_tel = st.text_input("WhatsApp")
        v_serv = st.selectbox("Serviço Realizado", ["Escova", "Progressiva", "Luzes", "Coloração", "Botox", "Corte", "Outros"])
        v_prof = st.selectbox("Atendida por", ["Eunides", "Evelyn"])
        v_valor = st.number_input("Valor Final (R$)", min_value=0.0, format="%.2f")
        if st.form_submit_button("CONCLUIR VENDA"):
            db.execute("INSERT INTO vendas (data, cliente, valor, servico, profissional) VALUES (?,?,?,?,?)",
                       (date.today().isoformat(), v_cli, v_valor, v_serv, v_prof))
            db.commit()
            disparar_whatsapp(v_cli, v_tel, v_serv, "", "agradecimento")
            st.balloons()

elif menu == "📉 Despesas":
    st.title("📉 Lançar Gastos do Salão")
    with st.form("gastos"):
        desc = st.text_input("O que foi comprado?")
        val = st.number_input("Valor (R$)", min_value=0.0)
        if st.form_submit_button("REGISTRAR DESPESA"):
            db.execute("INSERT INTO gastos (data, descricao, valor) VALUES (?,?,?)",
                       (date.today().isoformat(), desc, val))
            db.commit()
            st.error(f"Gasto de R$ {val} registrado.")

elif menu == "📊 Business Intelligence":
    st.title("📊 Desempenho Artmax")
    df_v = pd.read_sql("SELECT * FROM vendas", db)
    df_g = pd.read_sql("SELECT * FROM gastos", db)
    
    total_vendas = df_v['valor'].sum() if not df_v.empty else 0
    total_gastos = df_g['valor'].sum() if not df_g.empty else 0
    lucro = total_vendas - total_gastos
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Faturamento", f"R$ {total_vendas:.2f}")
    c2.metric("Gastos", f"R$ {total_gastos:.2f}")
    c3.metric("Lucro Real", f"R$ {lucro:.2f}", delta_color="normal")
    
    if not df_v.empty:
        fig = px.pie(df_v, values='valor', names='profissional', title="Vendas por Profissional",
                     color_discrete_sequence=[COLOR_GOLD, COLOR_PURPLE])
        st.plotly_chart(fig)