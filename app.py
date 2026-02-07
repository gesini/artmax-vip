import sqlite3
import pandas as pd
import streamlit as st
import urllib.parse
import plotly.express as px
from datetime import datetime, date, timedelta

# ==========================================
# DESIGN EXCLUSIVE (CONTRASTE PARA LEITURA)
# ==========================================
st.set_page_config(page_title="Artmax Exclusive VIP", layout="wide", page_icon="👑")

COLOR_PURPLE = "#6A0DAD" # Roxo Neon
COLOR_GOLD = "#FFD700"   # Ouro Puro
COLOR_BG = "#000000"     # Fundo Preto

def apply_ui():
    st.markdown(f"""
    <style>
    .stApp {{ background-color: {COLOR_BG}; color: #FFFFFF; }}
    
    /* Cabeçalho de Luxo */
    .logo-header {{
        background: linear-gradient(90deg, #1a0033, {COLOR_PURPLE}, #1a0033);
        padding: 35px; border-radius: 0 0 35px 35px;
        border-bottom: 4px solid {COLOR_GOLD}; text-align: center; margin-bottom: 25px;
    }}
    .logo-main {{ font-family: 'serif'; font-size: 55px; color: {COLOR_GOLD}; font-weight: bold; letter-spacing: 6px; }}

    /* CARTÕES BRANCOS (Visual da Imagem) */
    div[data-testid="stForm"], div[data-testid="stExpander"], .stTable {{
        background-color: #FFFFFF !important;
        padding: 25px !important;
        border-radius: 20px !important;
        color: #000000 !important;
        box-shadow: 0 8px 30px rgba(255, 255, 255, 0.1);
    }}

    /* Inputs e Labels de Alto Contraste */
    input, select, textarea, div[data-baseweb="select"] {{ 
        background-color: #F0F2F6 !important; 
        color: #000000 !important; 
        font-size: 20px !important; 
        font-weight: 900 !important;
    }}
    div[data-testid="stForm"] label {{ color: #000000 !important; font-size: 20px !important; font-weight: bold !important; }}
    
    /* Botões Luxo */
    .stButton>button {{
        width: 100%; border-radius: 15px; height: 65px;
        background: linear-gradient(90deg, {COLOR_PURPLE}, #6A0DAD) !important;
        color: #FFFFFF !important;
        border: 2px solid {COLOR_GOLD} !important;
        font-size: 22px !important; font-weight: bold;
    }}
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# BANCO DE DADOS
# ==========================================
def init_db():
    conn = sqlite3.connect("artmax_final_v10.db", check_same_thread=False)
    conn.execute("""CREATE TABLE IF NOT EXISTS agenda (
        id INTEGER PRIMARY KEY AUTOINCREMENT, data TEXT, hora TEXT, 
        cliente TEXT, telefone TEXT, servico TEXT, profissional TEXT)""")
    conn.execute("""CREATE TABLE IF NOT EXISTS vendas (
        id INTEGER PRIMARY KEY AUTOINCREMENT, data TEXT, cliente TEXT, 
        valor REAL, servico TEXT, profissional TEXT)""")
    conn.commit()
    return conn

db = init_db()

def disparar_whatsapp(nome, tel, servico, hora, tipo="confirmacao"):
    if tipo == "confirmacao":
        msg = f"Olá {nome}! ✨ Seu agendamento de {servico} na ARTMAX às {hora} foi confirmado. Já estamos te esperando! 💇‍♀️"
    elif tipo == "lembrete":
        msg = f"Olá {nome}! 🚨 Lembrete ARTMAX: seu atendimento de {servico} começa em 2 horas ({hora}). Já estamos prontos!"
    else:
        msg = f"Olá {nome}! ✨ Atendimento finalizado com sucesso. A ARTMAX agradece a preferência e te espera na próxima! 💜"
    
    tel_limpo = "".join(filter(str.isdigit, tel))
    link = f"https://wa.me/55{tel_limpo}?text={urllib.parse.quote(msg)}"
    # Abre em nova aba sem fechar o sistema
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

menu = st.sidebar.radio("MENU ARTMAX", ["📅 Agenda", "🤖 Robô Automático", "💰 Caixa", "📊 Lucros"])

# --- ABA 1: AGENDA ---
if menu == "📅 Agenda":
    st.title("Marcar e Gerenciar Atendimentos")
    with st.form("ag", clear_on_submit=True):
        c1, c2 = st.columns(2)
        cli = c1.text_input("Nome Cliente")
        tel = c2.text_input("WhatsApp (DDD+Número)")
        serv = st.selectbox("Serviço", ["Escova", "Progressiva", "Luzes", "Coloração", "Botox", "Corte"])
        prof = st.selectbox("Profissional", ["Eunides", "Evelyn"])
        c3, c4 = st.columns(2)
        dt = c3.date_input("Data", date.today())
        hr = c4.time_input("Hora")
        if st.form_submit_button("AGENDAR E NOTIFICAR CLIENTE"):
            db.execute("INSERT INTO agenda (data, hora, cliente, telefone, servico, profissional) VALUES (?,?,?,?,?,?)",
                       (dt.isoformat(), hr.strftime("%H:%M"), cli, tel, serv, prof))
            db.commit()
            disparar_whatsapp(cli, tel, serv, hr.strftime("%H:%M"), "confirmacao")

    st.divider()
    st.subheader("🗑️ Gerenciar Agenda do Dia")
    df_ag = pd.read_sql(f"SELECT * FROM agenda WHERE data = '{date.today().isoformat()}'", db)
    if not df_ag.empty:
        id_excluir = st.selectbox("Selecione para EXCLUIR:", df_ag['id'].tolist(), 
                                 format_func=lambda x: f"{df_ag[df_ag['id']==x]['hora'].values[0]} - {df_ag[df_ag['id']==x]['cliente'].values[0]}")
        if st.button("❌ APAGAR REGISTRO"):
            db.execute("DELETE FROM agenda WHERE id = ?", (id_excluir,))
            db.commit()
            st.rerun()
    st.table(df_ag[['hora', 'cliente', 'servico', 'profissional']])

# --- ABA 2: ROBÔ ---
elif menu == "🤖 Robô Automático":
    st.markdown("<div class='logo-header'><div class='logo-main'>ROBÔ ARTMAX</div></div>", unsafe_allow_html=True)
    hoje = date.today().isoformat()
    df_hoje = pd.read_sql("SELECT * FROM agenda WHERE data = ?", db, params=[hoje])
    if not df_hoje.empty:
        agora = datetime.now()
        for _, r in df_hoje.iterrows():
            horario = datetime.strptime(f"{hoje} {r['hora']}", "%Y-%m-%d %H:%M")
            diferenca = horario - agora
            if timedelta(hours=1) < diferenca <= timedelta(hours=2.5):
                st.warning(f"🚨 DISPARANDO AVISO: {r['cliente']}")
                if st.button(f"MANDAR MENSAGEM: {r['cliente']}"):
                    disparar_whatsapp(r['cliente'], r['telefone'], r['servico'], r['hora'], "lembrete")
            else:
                st.write(f"✅ {r['cliente']} - {r['hora']} (Aguardando prazo)")
    else: st.info("Sem atendimentos hoje.")

# --- ABA 3: CAIXA ---
elif menu == "💰 Caixa":
    st.title("Finalizar Atendimento")
    with st.form("venda"):
        v_cli = st.text_input("Cliente")
        v_tel = st.text_input("WhatsApp para Agradecimento")
        v_serv = st.selectbox("Serviço Realizado", ["Escova", "Progressiva", "Luzes", "Coloração", "Botox", "Corte"])
        v_prof = st.selectbox("Profissional", ["Eunides", "Evelyn"])
        v_valor = st.number_input("Valor Recebido (R$)", min_value=0.0)
        if st.form_submit_button("CONCLUIR E AGRADECER 💜"):
            db.execute("INSERT INTO vendas (data, cliente, valor, servico, profissional) VALUES (?,?,?,?,?)",
                       (date.today().isoformat(), v_cli, v_valor, v_serv, v_prof))
            db.commit()
            disparar_whatsapp(v_cli, v_tel, v_serv, "", "agradecimento")

# --- ABA 4: LUCROS ---
elif menu == "📊 Lucros":
    st.title("Resultados e Lucros")
    df_v = pd.read_sql("SELECT * FROM vendas", db)
    if not df_v.empty:
        c1, c2 = st.columns(2)
        c1.metric("FATURAMENTO BRUTO", f"R$ {df_v['valor'].sum():,.2f}")
        c2.metric("TOTAL ATENDIMENTOS", len(df_v))
        fig = px.bar(df_v, x="profissional", y="valor", color="profissional", barmode="group",
                     color_discrete_map={"Eunides": COLOR_GOLD, "Evelyn": COLOR_PURPLE})
        st.plotly_chart(fig, use_container_width=True)
        st.subheader("📝 Histórico Financeiro")
        st.table(df_v[['data', 'cliente', 'servico', 'profissional', 'valor']])
        id_venda = st.number_input("ID da Venda para apagar erro", min_value=1, step=1)
        if st.button("🗑️ APAGAR REGISTRO"):
            db.execute("DELETE FROM vendas WHERE id = ?", (id_venda,))
            db.commit()
            st.rerun()