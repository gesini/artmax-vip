import sqlite3
import pandas as pd
import streamlit as st
import urllib.parse
import plotly.express as px
from datetime import datetime, date, timedelta

# ==========================================
# DESIGN IMPERIAL (MÁXIMO CONTRASTE)
# ==========================================
st.set_page_config(page_title="Artmax Imperial VIP", layout="wide", page_icon="👑")

def apply_ui():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@800&family=Open+Sans:wght@700;800&display=swap');
    .stApp { background-color: #000000; color: #FFFFFF; font-family: 'Open Sans', sans-serif; }
    
    .header-box {
        background: linear-gradient(135deg, #4B0082, #6A0DAD);
        padding: 40px; border-radius: 0 0 40px 40px;
        border-bottom: 5px solid #FFD700; text-align: center; margin-bottom: 30px;
    }
    .main-title { font-family: 'Montserrat', sans-serif; font-size: 60px; color: #FFD700; font-weight: 800; text-shadow: 2px 2px #000; }
    
    /* FONTES GIGANTES */
    label, p, .stMarkdown { font-size: 26px !important; color: #FFD700 !important; font-weight: 800 !important; }
    
    /* INPUTS BRANCOS PARA LEITURA NO SOL */
    input, select, textarea, div[data-baseweb="select"] { 
        background-color: #FFFFFF !important; color: #000000 !important; 
        font-size: 24px !important; font-weight: 800 !important;
        border-radius: 15px !important; height: 65px !important;
    }

    .stButton>button {
        background: linear-gradient(90deg, #FFD700, #DAA520) !important;
        color: #000000 !important; border-radius: 20px; height: 80px;
        font-size: 28px !important; font-weight: 800 !important;
        border: 3px solid #FFFFFF !important;
    }
    
    div[data-testid="stForm"] {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 3px solid #6A0DAD !important; border-radius: 30px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# BANCO DE DADOS
# ==========================================
def init_db():
    conn = sqlite3.connect("artmax_imperial_v2.db", check_same_thread=False)
    conn.execute("CREATE TABLE IF NOT EXISTS agenda (id INTEGER PRIMARY KEY AUTOINCREMENT, data TEXT, hora TEXT, cliente TEXT, telefone TEXT, servico TEXT, profissional TEXT)")
    conn.execute("CREATE TABLE IF NOT EXISTS vendas (id INTEGER PRIMARY KEY AUTOINCREMENT, data TEXT, cliente TEXT, valor REAL, servico TEXT, profissional TEXT)")
    conn.execute("CREATE TABLE IF NOT EXISTS gastos (id INTEGER PRIMARY KEY AUTOINCREMENT, data TEXT, descricao TEXT, valor REAL)")
    conn.commit()
    return conn

db = init_db()

def disparar_whatsapp(nome, tel, servico, hora="", tipo="confirmacao"):
    if not tel: return
    mensagens = {
        "confirmacao": f"Olá, {nome}! ✨ Confirmamos seu horário na *Artmax* para *{servico}* às {hora}. Mal podemos esperar para te deixar maravilhosa! 👑💜",
        "lembrete": f"Oi, {nome}! ✨ Passando com carinho para lembrar do seu momento VIP hoje às {hora}. Já estamos te esperando! 🎀💇‍♀️",
        "agradecimento": f"Amamos te receber, {nome}! ✨ Esperamos que esteja se sentindo radiante. Obrigado por escolher a Artmax! 💜🙏"
    }
    msg = mensagens.get(tipo, "")
    tel_limpo = "".join(filter(str.isdigit, tel))
    link = f"https://wa.me/55{tel_limpo}?text={urllib.parse.quote(msg)}"
    st.components.v1.html(f"<script>window.open('{link}', '_blank');</script>", height=0)

# ==========================================
# INTERFACE
# ==========================================
apply_ui()

if "auth" not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    st.markdown("<div class='header-box'><div class='main-title'>ARTMAX</div><p style='color:#FFF; font-size:20px'>IMPERIAL SYSTEM</p></div>", unsafe_allow_html=True)
    u = st.text_input("USUÁRIO")
    s = st.text_input("SENHA", type="password")
    if st.button("ACESSAR SISTEMA"):
        if u.lower() == "artmax" and s == "gesini123":
            st.session_state.auth = True
            st.rerun()
    st.stop()

menu = st.sidebar.radio("NAVEGAR", ["📅 AGENDA", "🤖 ROBÔ", "💰 CAIXA", "📉 GASTOS", "📊 RELATÓRIOS"])

# --- AGENDA ---
if menu == "📅 AGENDA":
    st.markdown("### 👑 NOVO AGENDAMENTO")
    with st.form("ag", clear_on_submit=True):
        cli = st.text_input("NOME DA CLIENTE")
        tel = st.text_input("WHATSAPP (DDD+NÚMERO)")
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
            st.success("REGISTRADO!")

# --- GASTOS (ARRUMADO) ---
elif menu == "📉 GASTOS":
    st.title("📉 LANÇAR DESPESAS")
    with st.form("gastos"):
        desc = st.text_input("DESCRIÇÃO DO GASTO (EX: PRODUTOS)")
        val_g = st.number_input("VALOR R$", min_value=0.0)
        if st.form_submit_button("SALVAR GASTO"):
            db.execute("INSERT INTO gastos (data, descricao, valor) VALUES (?,?,?)",
                       (date.today().isoformat(), desc, val_g))
            db.commit()
            st.success("GASTO SALVO!")
    
    st.divider()
    df_g = pd.read_sql("SELECT * FROM gastos ORDER BY id DESC LIMIT 5", db)
    if df_g.empty:
        st.info("NENHUM GASTO LANÇADO AINDA. TUDO LIMPO! ✨")
    else:
        st.table(df_g[['data', 'descricao', 'valor']])

# --- RELATÓRIOS (ARRUMADO) ---
elif menu == "📊 RELATÓRIOS":
    st.title("📊 DESEMPENHO ARTMAX")
    df_v = pd.read_sql("SELECT * FROM vendas", db)
    df_g = pd.read_sql("SELECT * FROM gastos", db)
    
    receita = df_v['valor'].sum() if not df_v.empty else 0.0
    despesa = df_g['valor'].sum() if not df_g.empty else 0.0
    
    c1, c2, c3 = st.columns(3)
    c1.metric("FATURAMENTO", f"R$ {receita:,.2f}")
    c2.metric("GASTOS", f"R$ {despesa:,.2f}")
    c3.metric("LUCRO REAL", f"R$ {receita - despesa:,.2f}")

    if df_v.empty:
        st.warning("AGUARDANDO PRIMEIRAS VENDAS PARA GERAR O GRÁFICO... 🚀")
    else:
        fig = px.pie(df_v, values='valor', names='profissional', 
                     title="PRODUÇÃO POR PROFISSIONAL",
                     color_discrete_sequence=['#FFD700', '#6A0DAD'])
        st.plotly_chart(fig, use_container_width=True)

# (Outras abas como Robô e Caixa seguem a mesma lógica imperial)