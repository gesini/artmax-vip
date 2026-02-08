import sqlite3
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
import urllib.parse
import plotly.express as px
from datetime import date

# ==========================================
# CONFIG
# ==========================================
st.set_page_config(page_title="Artmax Exclusive VIP", layout="wide", page_icon="👑")

# ==========================================
# PALETA SUAVE / PREMIUM
# ==========================================
COLOR_PURPLE = "#B79CED"        # lilás suave
COLOR_DEEP_PURPLE = "#6D5BD0"   # roxo fechado suave
COLOR_GOLD = "#E6C97A"          # dourado suave
COLOR_DARK_BG = "#0B1020"       # fundo escuro elegante
COLOR_CARD_BG = "rgba(255,255,255,0.06)"
COLOR_BORDER = "rgba(230, 201, 122, 0.22)"

COMMISSION_RATE = 0.50  # 50%

def apply_ui():
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Poppins:wght@300;400;600&display=swap');

    .stApp {{
        background-color: {COLOR_DARK_BG};
        color: #FFFFFF;
        font-family: 'Poppins', sans-serif;
    }}

    /* HEADER */
    .logo-header {{
        background: linear-gradient(135deg, {COLOR_DEEP_PURPLE}, {COLOR_PURPLE});
        padding: 34px;
        border-radius: 0 0 42px 42px;
        border-bottom: 4px solid {COLOR_GOLD};
        text-align: center;
        box-shadow: 0 10px 26px rgba(0,0,0,0.45);
        margin-bottom: 22px;
    }}
    .logo-main {{
        font-family: 'Playfair Display', serif;
        font-size: 56px;
        color: {COLOR_GOLD};
        font-weight: 700;
        letter-spacing: 4px;
    }}
    .logo-sub {{
        font-size: 16px;
        color: rgba(255,255,255,0.78);
        letter-spacing: 2px;
        text-transform: uppercase;
    }}

    /* CARDS */
    div[data-testid="stForm"], div[data-testid="stExpander"], .stTable, div[data-testid="stMetric"] {{
        background: {COLOR_CARD_BG} !important;
        backdrop-filter: blur(10px);
        padding: 22px !important;
        border-radius: 20px !important;
        border: 1px solid {COLOR_BORDER} !important;
        color: #FFFFFF !important;
    }}

    /* INPUTS MAIS SUAVES */
    input, textarea, div[data-baseweb="select"] {{
        background-color: rgba(255,255,255,0.88) !important;
        color: #111827 !important;
        border-radius: 12px !important;
        font-size: 16px !important;
        font-weight: 500 !important;
    }}

    /* BOTÕES */
    .stButton>button {{
        background: linear-gradient(90deg, {COLOR_GOLD}, #D9B85F) !important;
        color: #0B1020 !important;
        border: none !important;
        border-radius: 14px;
        height: 52px;
        font-weight: 700;
        transition: 0.25s;
        text-transform: uppercase;
    }}
    .stButton>button:hover {{
        transform: scale(1.015);
        box-shadow: 0 6px 18px rgba(230, 201, 122, 0.25);
    }}

    /* SIDEBAR PREMIUM */
    section[data-testid="stSidebar"] {{
        background: linear-gradient(180deg, rgba(109,91,208,0.22), rgba(11,16,32,0.92)) !important;
        border-right: 1px solid rgba(230,201,122,0.16);
    }}
    section[data-testid="stSidebar"] * {{
        color: rgba(255,255,255,0.92) !important;
    }}
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# DB
# ==========================================
def init_db():
    conn = sqlite3.connect("artmax_final_v12.db", check_same_thread=False)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS agenda (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT,
            hora TEXT,
            cliente TEXT,
            telefone TEXT,
            servico TEXT,
            profissional TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS vendas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT,
            cliente TEXT,
            valor REAL,
            servico TEXT,
            profissional TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS gastos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT,
            descricao TEXT,
            valor REAL
        )
    """)
    conn.commit()
    return conn

db = init_db()

# ==========================================
# WHATSAPP
# ==========================================
def build_whatsapp_link(nome, tel, servico, hora="", tipo="confirmacao"):
    if not tel:
        return None

    mensagens = {
        "confirmacao": f"Olá {nome}! ✨ Confirmamos seu horário para *{servico}* às {hora}. A Artmax Exclusive te espera!",
        "lembrete": f"Oi {nome}! 👑 Passando para lembrar do seu momento VIP hoje às {hora} ({servico}). Até logo!",
        "agradecimento": f"Foi um prazer te atender, {nome}! ✨ Esperamos que tenha amado o resultado do seu *{servico}*. Até a próxima! 💜"
    }
    msg = mensagens.get(tipo, "")
    tel_limpo = "".join(filter(str.isdigit, tel))
    if not tel_limpo:
        return None

    return f"https://wa.me/55{tel_limpo}?text={urllib.parse.quote(msg)}"

def disparar_whatsapp(link):
    if not link:
        return
    # tenta abrir em nova aba (pode ser bloqueado pelo navegador)
    components.html(f"<script>window.open('{link}', '_blank');</script>", height=0)

# ==========================================
# APP
# ==========================================
apply_ui()

def header():
    st.markdown(
        "<div class='logo-header'><div class='logo-main'>ARTMAX</div><div class='logo-sub'>Exclusive VIP</div></div>",
        unsafe_allow_html=True
    )

# AUTH
if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    header()
    with st.container():
        st.caption("Acesso restrito — painel interno.")
        u = st.text_input("Username")
        s = st.text_input("Password", type="password")
        if st.button("ENTER SYSTEM"):
            if u.lower().strip() == "artmax" and s.strip() == "gesini123":
                st.session_state.auth = True
                st.rerun()
            else:
                st.error("Usuário ou senha incorretos.")
    st.stop()

# HEADER SEMPRE
header()

# MENU
menu = st.sidebar.radio(
    "Navegação",
    ["📅 Agenda", "🤖 Robô VIP", "💰 Checkout", "📉 Despesas", "📊 Business Intelligence"]
)

# ==========================================
# 📅 AGENDA
# ==========================================
if menu == "📅 Agenda":
    st.markdown("### 📅 Novo Agendamento")
    st.caption("Crie agendamentos e mande confirmação automática via WhatsApp.")

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
            if not cli.strip():
                st.error("Informe o nome da cliente.")
                st.stop()
            if not tel.strip():
                st.error("Informe o WhatsApp.")
                st.stop()

            db.execute(
                "INSERT INTO agenda (data, hora, cliente, telefone, servico, profissional) VALUES (?,?,?,?,?,?)",
                (dt.isoformat(), hr.strftime("%H:%M"), cli.strip(), tel.strip(), serv, prof)
            )
            db.commit()

            link = build_whatsapp_link(cli.strip(), tel.strip(), serv, hr.strftime("%H:%M"), "confirmacao")
            disparar_whatsapp(link)

            st.success(f"Agendado com sucesso para {cli}!")
            if link:
                st.link_button("Abrir WhatsApp (caso não tenha aberto)", link)

    st.markdown("### 📌 Próximos agendamentos")
    df_next = pd.read_sql(
        "SELECT * FROM agenda WHERE data >= ? ORDER BY data, hora LIMIT 30",
        db,
        params=[date.today().isoformat()]
    )
    if df_next.empty:
        st.info("Nenhum agendamento futuro cadastrado ainda.")
    else:
        st.dataframe(df_next, use_container_width=True)

# ==========================================
# 🤖 ROBÔ VIP
# ==========================================
elif menu == "🤖 Robô VIP":
    st.title("🤖 Monitoramento de Horários")
    st.caption("Envie lembretes das clientes do dia com 1 clique.")

    hoje = date.today().isoformat()
    df = pd.read_sql("SELECT * FROM agenda WHERE data = ? ORDER BY hora", db, params=[hoje])

    if df.empty:
        st.info("Nenhuma cliente para hoje ainda.")
    else:
        for _, r in df.iterrows():
            st.write(f"📌 **{r['hora']}** — **{r['cliente']}** • {r['servico']} • {r['profissional']}")
            cols = st.columns([1, 2])
            if cols[0].button(f"Enviar Lembrete", key=f"lem_{r['id']}"):
                link = build_whatsapp_link(r["cliente"], r["telefone"], r["servico"], r["hora"], "lembrete")
                disparar_whatsapp(link)
                if link:
                    cols[1].link_button("Abrir WhatsApp (fallback)", link)

# ==========================================
# 💰 CHECKOUT
# ==========================================
elif menu == "💰 Checkout":
    st.title("💰 Finalizar Atendimento")
    st.caption("Registre a venda e envie mensagem de agradecimento automática.")

    with st.form("caixa", clear_on_submit=True):
        v_cli = st.text_input("Nome da Cliente")
        v_tel = st.text_input("WhatsApp")
        v_serv = st.selectbox("Serviço Realizado", ["Escova", "Progressiva", "Luzes", "Coloração", "Botox", "Corte", "Outros"])
        v_prof = st.selectbox("Atendida por", ["Eunides", "Evelyn"])
        v_valor = st.number_input("Valor Final (R$)", min_value=0.0, format="%.2f")

        if st.form_submit_button("CONCLUIR VENDA"):
            if not v_cli.strip():
                st.error("Informe o nome da cliente.")
                st.stop()
            if v_valor <= 0:
                st.error("Informe um valor maior que 0.")
                st.stop()

            db.execute(
                "INSERT INTO vendas (data, cliente, valor, servico, profissional) VALUES (?,?,?,?,?)",
                (date.today().isoformat(), v_cli.strip(), float(v_valor), v_serv, v_prof)
            )
            db.commit()

            link = build_whatsapp_link(v_cli.strip(), v_tel.strip(), v_serv, "", "agradecimento")
            disparar_whatsapp(link)

            st.success("Venda registrada com sucesso.")
            if link:
                st.link_button("Abrir WhatsApp (caso não tenha aberto)", link)
            st.balloons()

# ==========================================
# 📉 DESPESAS
# ==========================================
elif menu == "📉 Despesas":
    st.title("📉 Lançar Gastos do Salão")
    st.caption("Controle de despesas para cálculo do lucro real.")

    with st.form("gastos", clear_on_submit=True):
        desc = st.text_input("O que foi comprado?")
        val = st.number_input("Valor (R$)", min_value=0.0, format="%.2f")

        if st.form_submit_button("REGISTRAR DESPESA"):
            if not desc.strip():
                st.error("Descreva o gasto (ex.: shampoo, reposição, aluguel...).")
                st.stop()
            if val <= 0:
                st.error("Informe um valor maior que 0.")
                st.stop()

            db.execute(
                "INSERT INTO gastos (data, descricao, valor) VALUES (?,?,?)",
                (date.today().isoformat(), desc.strip(), float(val))
            )
            db.commit()

            st.success(f"Despesa registrada: R$ {val:.2f}")

    st.markdown("### 📌 Últimas despesas")
    df_g_last = pd.read_sql("SELECT * FROM gastos ORDER BY data DESC, id DESC LIMIT 20", db)
    if df_g_last.empty:
        st.info("Nenhuma despesa cadastrada ainda.")
    else:
        st.dataframe(df_g_last, use_container_width=True)

# ==========================================
# 📊 BUSINESS INTELLIGENCE
# ==========================================
elif menu == "📊 Business Intelligence":
    st.title("📊 Desempenho Artmax")
    st.caption("Faturamento, gastos, comissão (50%) e lucro real.")

    df_v = pd.read_sql("SELECT * FROM vendas", db)
    df_g = pd.read_sql("SELECT * FROM gastos", db)

    if not df_v.empty:
        df_v["valor"] = pd.to_numeric(df_v["valor"], errors="coerce").fillna(0.0)
    if not df_g.empty:
        df_g["valor"] = pd.to_numeric(df_g["valor"], errors="coerce").fillna(0.0)

    total_vendas = float(df_v["valor"].sum()) if not df_v.empty else 0.0
    total_gastos = float(df_g["valor"].sum()) if not df_g.empty else 0.0
    total_comissao = total_vendas * COMMISSION_RATE
    lucro = total_vendas - total_gastos - total_comissao

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Faturamento", f"R$ {total_vendas:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    c2.metric("Gastos", f"R$ {total_gastos:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    c3.metric("Comissão (50%)", f"R$ {total_comissao:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    c4.metric("Lucro Real", f"R$ {lucro:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."), delta_color="normal")

    st.markdown("### 💎 Resumo por Profissional")
    if df_v.empty:
        st.info("Sem vendas cadastradas ainda.")
    else:
        resumo = (
            df_v.groupby("profissional", as_index=False)["valor"]
              .sum()
              .rename(columns={"valor": "vendas"})
        )
        resumo["comissao_50"] = resumo["vendas"] * COMMISSION_RATE
        resumo["liquido_pos_comissao"] = resumo["vendas"] - resumo["comissao_50"]

        st.dataframe(resumo, use_container_width=True)

        fig = px.pie(
            resumo,
            values="vendas",
            names="profissional",
            title="Vendas por Profissional",
            color_discrete_sequence=["#E6C97A", "#B79CED", "#6D5BD0", "#A8E6CF"]
        )
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("### 🧾 Últimas vendas")
        df_last = df_v.sort_values(["data", "id"], ascending=[False, False]).head(25)
        st.dataframe(df_last, use_container_width=True)
