import sqlite3
import pandas as pd
import streamlit as st
import urllib.parse
import plotly.express as px
from datetime import datetime, date, timedelta

# ==========================================
# DESIGN ELITE (PRETO, ROXO E OURO) - LETRAS GIGANTES
# ==========================================
st.set_page_config(page_title="Artmax Pro Business", layout="wide", page_icon="👑")

def apply_ui():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@800&family=Open+Sans:wght@700;800&display=swap');
    .stApp { background-color: #000000; color: #FFFFFF; font-family: 'Open Sans', sans-serif; }
    
    .header-box {
        background: linear-gradient(135deg, #4B0082, #6A0DAD);
        padding: 30px; border-radius: 0 0 30px 30px;
        border-bottom: 5px solid #FFD700; text-align: center; margin-bottom: 20px;
    }
    .main-title { font-family: 'Montserrat', sans-serif; font-size: 55px; color: #FFD700; font-weight: 800; }
    
    /* FONTES GIGANTES PARA CELULAR */
    label, p, .stMarkdown { font-size: 28px !important; color: #FFD700 !important; font-weight: 800 !important; }
    
    /* INPUTS BRANCOS (MÁXIMA LEITURA) */
    input, select, textarea, div[data-baseweb="select"] { 
        background-color: #FFFFFF !important; color: #000000 !important; 
        font-size: 26px !important; font-weight: 800 !important;
        border-radius: 12px !important; height: 65px !important;
    }

    .stButton>button {
        background: linear-gradient(90deg, #FFD700, #DAA520) !important;
        color: #000000 !important; border-radius: 15px; height: 85px;
        font-size: 30px !important; font-weight: 800 !important;
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
    conn = sqlite3.connect("artmax_final_v99.db", check_same_thread=False)
    conn.execute("CREATE TABLE IF NOT EXISTS agenda (id INTEGER PRIMARY KEY AUTOINCREMENT, data TEXT, hora TEXT, cliente TEXT, telefone TEXT, servico TEXT, profissional TEXT)")
    conn.execute("CREATE TABLE IF NOT EXISTS vendas (id INTEGER PRIMARY KEY AUTOINCREMENT, data TEXT, cliente TEXT, valor REAL, servico TEXT, profissional TEXT)")
    conn.execute("CREATE TABLE IF NOT EXISTS gastos (id INTEGER PRIMARY KEY AUTOINCREMENT, data TEXT, descricao TEXT, valor REAL)")
    conn.commit()
    return conn

db = init_db()

def disparar_whatsapp(nome, tel, servico, hora="", tipo="confirmacao"):
    if not tel: return
    mensagens = {
        "confirmacao": f"Olá {nome}! ✨ Confirmamos seu horário na *Artmax* para *{servico}* às {hora}. Mal podemos esperar para te deixar maravilhosa! 👑💜",
        "lembrete": f"Oi {nome}! ✨ Passando com todo carinho para lembrar que seu momento VIP na Artmax é hoje, às {hora}. Já estamos te esperando! 🎀💇‍♀️",
        "agradecimento": f"Amamos te receber hoje, {nome}! ✨ Esperamos que você se sinta radiante. Obrigado por escolher a Artmax! Beijos e até a próxima! 💜🙏"
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
    st.markdown("<div class='header-box'><div class='main-title'>ARTMAX PRO</div></div>", unsafe_allow_html=True)
    u = st.text_input("USUÁRIO")
    s = st.text_input("SENHA", type="password")
    if st.button("ACESSAR"):
        if u.lower() == "artmax" and s == "gesini123":
            st.session_state.auth = True
            st.rerun()
    st.stop()

menu = st.sidebar.radio("MENU", ["📅 AGENDA", "🤖 ROBÔ", "💰 CAIXA", "📉 GASTOS", "📊 RELATÓRIOS & COMISSÃO"])

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
            st.success("AGENDADO!")

# --- ROBÔ ---
elif menu == "🤖 ROBÔ":
    st.title("🤖 LEMBRETES DO DIA")
    hoje = date.today().isoformat()
    df = pd.read_sql("SELECT * FROM agenda WHERE data = ?", db, params=[hoje])
    if df.empty:
        st.info("NENHUMA CLIENTE PARA HOJE AINDA. ✨")
    else:
        for _, r in df.iterrows():
            st.write(f"⭐ **{r['hora']}** - {r['cliente']} ({r['servico']})")
            if st.button(f"AVISAR: {r['cliente']}", key=r['id']):
                disparar_whatsapp(r['cliente'], r['telefone'], r['servico'], r['hora'], "lembrete")

# --- CAIXA ---
elif menu == "💰 CAIXA":
    st.title("💰 FINALIZAR ATENDIMENTO")
    with st.form("cx", clear_on_submit=True):
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
            st.success("VENDA REGISTRADA!")

# --- GASTOS ---
elif menu == "📉 GASTOS":
    st.title("📉 LANÇAR DESPESAS")
    with st.form("gs"):
        desc = st.text_input("DESCRIÇÃO DO GASTO")
        val = st.number_input("VALOR R$", min_value=0.0)
        if st.form_submit_button("SALVAR GASTO"):
            db.execute("INSERT INTO gastos (data, descricao, valor) VALUES (?,?,?)", (date.today().isoformat(), desc, val))
            db.commit()
            st.success("GASTO SALVO!")
    df_g = pd.read_sql("SELECT * FROM gastos ORDER BY id DESC LIMIT 5", db)
    if df_g.empty:
        st.info("NENHUM GASTO LANÇADO AINDA. TUDO LIMPO! ✨")
    else:
        st.table(df_g[['data', 'descricao', 'valor']])

# --- RELATÓRIOS E COMISSÃO ---
elif menu == "📊 RELATÓRIOS & COMISSÃO":
    st.title("📊 FINANCEIRO E COMISSÕES")
    df_v = pd.read_sql("SELECT * FROM vendas", db)
    df_g = pd.read_sql("SELECT * FROM gastos", db)
    
    total = df_v['valor'].sum() if not df_v.empty else 0.0
    gastos = df_g['valor'].sum() if not df_g.empty else 0.0
    
    c1, c2, c3 = st.columns(3)
    c1.metric("FATURAMENTO", f"R$ {total:.2f}")
    c2.metric("GASTOS", f"R$ {gastos:.2f}")
    c3.metric("LUCRO LÍQUIDO", f"R$ {total - gastos:.2f}")

    st.divider()
    st.subheader("💰 COMISSÃO DA EVELYN (50%)")
    if df_v.empty:
        st.info("SEM VENDAS PARA CALCULAR COMISSÕES AINDA. 🚀")
    else:
        vendas_ev = df_v[df_v['profissional'] == 'Evelyn']['valor'].sum()
        st.warning(f"TOTAL EVELYN: R$ {vendas_ev:.2f} | COMISSÃO (50%): R$ {vendas_ev * 0.5:.2f}")
        fig = px.pie(df_v, values='valor', names='profissional', color_discrete_sequence=['#FFD700', '#6A0DAD'])
        st.plotly_chart(fig, use_container_width=True)