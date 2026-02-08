import sqlite3
import pandas as pd
import streamlit as st
import urllib.parse
from datetime import datetime, date, timedelta

# ==========================================
# DESIGN IMPERIAL (ROXO, PRETO E OURO)
# ==========================================
st.set_page_config(page_title="Artmax Imperial VIP", layout="wide", page_icon="👑")

def apply_ui():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@700;800&family=Open+Sans:wght@600;800&display=swap');

    /* Fundo e Texto Geral */
    .stApp { background-color: #000000; color: #FFFFFF; font-family: 'Open Sans', sans-serif; }
    
    /* Cabeçalho de Elite */
    .header-box {
        background: linear-gradient(135deg, #4B0082, #6A0DAD);
        padding: 50px; border-radius: 0 0 40px 40px;
        border-bottom: 5px solid #FFD700; text-align: center; margin-bottom: 30px;
    }
    .main-title { font-family: 'Montserrat', sans-serif; font-size: 65px; color: #FFD700; font-weight: 800; text-shadow: 2px 2px #000; }
    
    /* FONTES GRANDES NOS INPUTS E LABELS */
    label, p, .stMarkdown { font-size: 24px !important; color: #FFD700 !important; font-weight: 800 !important; }
    
    /* Caixas de Seleção e Inputs Brancos (Máxima Leitura) */
    input, select, textarea, div[data-baseweb="select"] { 
        background-color: #FFFFFF !important; 
        color: #000000 !important; 
        font-size: 22px !important; 
        font-weight: 800 !important;
        border-radius: 15px !important;
        height: 60px !important;
    }

    /* Botões Dourados de Luxo */
    .stButton>button {
        background: linear-gradient(90deg, #FFD700, #DAA520) !important;
        color: #000000 !important; border-radius: 20px; height: 70px;
        font-size: 26px !important; font-weight: 800 !important;
        border: 2px solid #FFFFFF !important; margin-top: 20px;
    }

    /* Tabelas e Cards */
    div[data-testid="stForm"] {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 2px solid #6A0DAD !important; border-radius: 30px !important;
        padding: 30px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# BANCO DE DADOS E LÓGICA
# ==========================================
def init_db():
    conn = sqlite3.connect("artmax_imperial.db", check_same_thread=False)
    conn.execute("CREATE TABLE IF NOT EXISTS agenda (id INTEGER PRIMARY KEY AUTOINCREMENT, data TEXT, hora TEXT, cliente TEXT, telefone TEXT, servico TEXT, profissional TEXT)")
    conn.execute("CREATE TABLE IF NOT EXISTS vendas (id INTEGER PRIMARY KEY AUTOINCREMENT, data TEXT, cliente TEXT, valor REAL, servico TEXT, profissional TEXT)")
    conn.execute("CREATE TABLE IF NOT EXISTS gastos (id INTEGER PRIMARY KEY AUTOINCREMENT, data TEXT, descricao TEXT, valor REAL)")
    conn.commit()
    return conn

db = init_db()

def disparar_whatsapp(nome, tel, servico, hora="", tipo="confirmacao"):
    if not tel: return
    
    # MENSAGENS CARINHOSAS E PROFISSIONAIS
    mensagens = {
        "confirmacao": f"Olá, {nome}! ✨ É um prazer confirmar seu horário na *Artmax Exclusive*. Agendamos seu(sua) *{servico}* para as {hora}. Mal podemos esperar para te deixar ainda mais maravilhosa! 👑💜",
        "lembrete": f"Oi, {nome}! ✨ Passando com todo carinho para lembrar que seu momento VIP na Artmax é hoje, às {hora}. Já estamos preparando tudo para você! Até logo! 🎀💇‍♀️",
        "agradecimento": f"Amamos te receber hoje, {nome}! ✨ Esperamos que você se sinta radiante com seu novo visual. Obrigado por escolher a Artmax! Beijos e até a próxima! 💜🙏"
    }
    
    msg = mensagens.get(tipo, "")
    tel_limpo = "".join(filter(str.isdigit, tel))
    link = f"https://wa.me/55{tel_limpo}?text={urllib.parse.quote(msg)}"
    st.components.v1.html(f"<script>window.open('{link}', '_blank');</script>", height=0)

# ==========================================
# INTERFACE PRINCIPAL
# ==========================================
apply_ui()

if "auth" not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    st.markdown("<div class='header-box'><div class='main-title'>ARTMAX</div><p style='color:#FFF'>IMPERIAL SYSTEM</p></div>", unsafe_allow_html=True)
    u = st.text_input("USUÁRIO")
    s = st.text_input("SENHA", type="password")
    if st.button("ACESSAR SISTEMA"):
        if u.lower() == "artmax" and s == "gesini123":
            st.session_state.auth = True
            st.rerun()
    st.stop()

menu = st.sidebar.radio("NAVEGAR", ["📅 AGENDA", "🤖 ROBÔ ARTMAX", "💰 CAIXA", "📉 GASTOS", "📊 RELATÓRIOS"])

if menu == "📅 AGENDA":
    st.markdown("### 👑 NOVO AGENDAMENTO")
    with st.form("ag", clear_on_submit=True):
        cli = st.text_input("NOME DA CLIENTE")
        tel = st.text_input("WHATSAPP (COM DDD)")
        serv = st.selectbox("SERVIÇO", ["Escova", "Progressiva", "Luzes", "Coloração", "Botox", "Corte", "Outros"])
        prof = st.radio("PROFISSIONAL", ["Eunides", "Evelyn"], horizontal=True)
        c1, c2 = st.columns(2)
        dt = c1.date_input("DATA", date.today())
        hr = c2.time_input("HORÁRIO")
        if st.form_submit_button("SALVAR E NOTIFICAR"):
            db.execute("INSERT INTO agenda (data, hora, cliente, telefone, servico, profissional) VALUES (?,?,?,?,?,?)",
                       (dt.isoformat(), hr.strftime("%H:%M"), cli, tel, serv, prof))
            db.commit()
            disparar_whatsapp(cli, tel, serv, hr.strftime("%H:%M"), "confirmacao")
            st.success("AGENDADO!")

elif menu == "🤖 ROBÔ ARTMAX":
    st.title("🤖 LEMBRETES DO DIA")
    hoje = date.today().isoformat()
    df = pd.read_sql("SELECT * FROM agenda WHERE data = ?", db, params=[hoje])
    if df.empty:
        st.info("Agenda vazia para hoje.")
    else:
        for _, r in df.iterrows():
            st.write(f"⭐ **{r['hora']}** - {r['cliente']} ({r['servico']})")
            if st.button(f"MANDAR CARINHO: {r['cliente']}", key=r['id']):
                disparar_whatsapp(r['cliente'], r['telefone'], r['servico'], r['hora'], "lembrete")

elif menu == "💰 CAIXA":
    st.title("💰 FINALIZAR ATENDIMENTO")
    with st.form("caixa"):
        v_cli = st.text_input("NOME DA CLIENTE")
        v_tel = st.text_input("WHATSAPP")
        v_serv = st.selectbox("SERVIÇO FEITO", ["Escova", "Progressiva", "Luzes", "Coloração", "Botox", "Corte", "Outros"])
        v_prof = st.radio("QUEM ATENDEU?", ["Eunides", "Evelyn"], horizontal=True)
        v_val = st.number_input("VALOR TOTAL R$", min_value=0.0)
        if st.form_submit_button("CONCLUIR E AGRADECER"):
            db.execute("INSERT INTO vendas (data, cliente, valor, servico, profissional) VALUES (?,?,?,?,?)",
                       (date.today().isoformat(), v_cli, v_val, v_serv, v_prof))
            db.commit()
            disparar_whatsapp(v_cli, v_tel, v_serv, "", "agradecimento")