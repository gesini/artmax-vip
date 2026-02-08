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

# Coloque sua logo na mesma pasta do app com este nome:
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

    /* Header premium */
    .app-header {{
        background: linear-gradient(135deg, rgba(74,0,224,0.60), rgba(142,45,226,0.35));
        border: 1px solid {C_GOLD_SOFT};
        padding: 18px 22px;
        border-radius: 20px;
        margin-bottom: 16px;
        box-shadow: 0 16px 40px rgba(0,0,0,0.45);
        position: relative;
        overflow: hidden;
    }}
    .app-header:before {{
        content: "";
        position: absolute;
        inset: -60%;
        background: radial-gradient(circle, rgba(212,175,55,0.12), rgba(255,255,255,0.0) 60%);
        transform: rotate(10deg);
        pointer-events: none;
    }}
    .app-title {{
        font-family: 'Playfair Display', serif;
        font-size: 28px;
        font-weight: 700;
        letter-spacing: 0.4px;
        color: {C_WHITE};
        margin: 0;
        line-height: 1.15;
        text-shadow: 0 10px 24px rgba(0,0,0,0.45);
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

    /* Cards / forms */
    div[data-testid="stForm"], div[data-testid="stExpander"], div[data-testid="stMetric"] {{
        background: {C_SURFACE} !important;
        border: 1px solid {C_GOLD_SOFT} !important;
        border-radius: 20px !important;
        padding: 18px !important;
        color: {C_TEXT} !important;
        backdrop-filter: blur(10px);
    }}

    /* Dataframes */
    div[data-testid="stDataFrame"] {{
        background: {C_SURFACE_2} !important;
        border: 1px solid rgba(255,255,255,0.10) !important;
        border-radius: 18px !important;
        padding: 10px !important;
        backdrop-filter: blur(10px);
    }}

    /* FIX do card apagado (st.metric) */
    div[data-testid="stMetric"] * {{
        color: {C_TEXT} !important;
        opacity: 1 !important;
        filter: none !important;
    }}
    div[data-testid="stMetric"] label, div[data-testid="stMetric"] small {{
        color: {C_MUTED} !important;
    }}

    /* Inputs */
    input, textarea, div[data-baseweb="select"] {{
        background-color: rgba(255,255,255,0.92) !important;
        color: #101018 !important;
        border-radius: 14px !important;
        font-size: 14px !important;
        font-weight: 500 !important;
    }}

    /* Buttons com glow */
    .stButton>button {{
        background: linear-gradient(90deg, {C_GOLD}, #B8860B) !important;
        color: #0B0B10 !important;
        border: 1px solid rgba(212,175,55,0.45) !important;
        border-radius: 14px;
        height: 48px;
        font-weight: 800;
        transition: 0.18s ease;
        text-transform: none;
        box-shadow:
          0 10px 26px rgba(212,175,55,0.16),
          0 0 0 rgba(142,45,226,0.0);
    }}
    .stButton>button:hover {{
        transform: translateY(-1px);
        box-shadow:
          0 14px 34px rgba(212,175,55,0.22),
          0 0 24px rgba(142,45,226,0.20);
    }}

    /* Sidebar elegante */
    section[data-testid="stSidebar"] {{
        background: linear-gradient(180deg, rgba(74,0,224,0.22), rgba(11,11,16,0.96)) !important;
        border-right: 1px solid rgba(212,175,55,0.16);
    }}
    section[data-testid="stSidebar"] * {{
        color: {C_TEXT} !important;
    }}

    /* Login central */
    .login-wrap {{
        display: flex;
        justify-content: center;
        align-items: center;
        padding-top: 40px;
    }}
    .login-card {{
        width: 480px;
        max-width: 92vw;
        background: {C_SURFACE};
        border: 1px solid {C_GOLD_SOFT};
        border-radius: 22px;
        padding: 22px 22px 16px 22px;
        box-shadow: 0 22px 60px rgba(0,0,0,0.55);
        backdrop-filter: blur(12px);
    }}
    .login-title {{
        font-family: 'Playfair Display', serif;
        font-size: 26px;
        font-weight: 700;
        color: {C_WHITE};
        margin: 0 0 6px 0;
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

def logo_exists() -> bool:
    return Path(LOGO_PATH).exists()

def show_logo(where="main", width=260):
    if logo_exists():
        if where == "sidebar":
            st.sidebar.image(LOGO_PATH, use_container_width=True)
        else:
            st.image(LOGO_PATH, width=width)

# =========================================================
# REGRA: comissão só da Evelyn (50% do que ela fizer)
# =========================================================
def calc_comissao(profissional: str, valor_venda: float) -> float:
    if profissional.strip().lower() == "evelyn":
        return float(valor_venda) * 0.5
    return 0.0

# =========================================================
# FUNÇÕES DE MÊS/ANO (controle mês a mês)
# =========================================================
MESES_PT = [
    "Janeiro","Fevereiro","Março","Abril","Maio","Junho",
    "Julho","Agosto","Setembro","Outubro","Novembro","Dezembro"
]

def month_range(year: int, month: int):
    start = date(year, month, 1)
    if month == 12:
        end = date(year + 1, 1, 1)
    else:
        end = date(year, month + 1, 1)
    return start, end  # [start, end)

def date_iso(d: date) -> str:
    return d.isoformat()

# =========================================================
# DB + MIGRAÇÃO
# =========================================================
def init_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)

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
            profissional TEXT,
            comissao REAL DEFAULT 0
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

    cols = [r[1] for r in conn.execute("PRAGMA table_info(vendas)").fetchall()]
    if "comissao" not in cols:
        conn.execute("ALTER TABLE vendas ADD COLUMN comissao REAL DEFAULT 0")

    conn.commit()
    return conn

db = init_db()

# =========================================================
# WhatsApp
# =========================================================
def build_whatsapp_link(nome, tel, servico, hora="", tipo="confirmacao"):
    if not tel:
        return None
    msgs = {
        "confirmacao": f"Olá {nome}! ✨ Confirmamos seu horário para {servico} às {hora}.",
        "lembrete": f"Oi {nome}! 💜 Lembrete do seu horário hoje às {hora} ({servico}).",
        "agradecimento": f"Obrigada pela preferência, {nome}! ✨ Foi um prazer atender você ({servico})."
    }
    msg = msgs.get(tipo, "")
    tel_limpo = "".join(filter(str.isdigit, tel))
    if not tel_limpo:
        return None
    return f"https://wa.me/55{tel_limpo}?text={urllib.parse.quote(msg)}"

def open_whatsapp(link):
    if not link:
        return
    components.html(f"<script>window.open('{link}', '_blank');</script>", height=0)

# =========================================================
# APP
# =========================================================
apply_ui()

if "auth" not in st.session_state:
    st.session_state.auth = False

# Esconde sidebar na tela de login
if not st.session_state.auth:
    st.markdown(
        "<style>section[data-testid='stSidebar']{display:none !important;}</style>",
        unsafe_allow_html=True
    )

if not st.session_state.auth:
    st.markdown("<div class='login-wrap'><div class='login-card'>", unsafe_allow_html=True)

    if logo_exists():
        st.image(LOGO_PATH, use_container_width=True)

    st.markdown(f"<div class='login-title'>{APP_NAME}</div>", unsafe_allow_html=True)
    st.markdown("<div class='login-sub'>Acesso restrito ao sistema interno.</div>", unsafe_allow_html=True)

    u = st.text_input("Usuário", placeholder="Digite seu usuário")
    s = st.text_input("Senha", type="password", placeholder="Digite sua senha")

    colA, colB = st.columns([1, 1])
    with colA:
        entrar = st.button("Entrar")
    with colB:
        st.caption("")

    if entrar:
        if u.strip().lower() == "artmax" and s.strip() == "gesini123":
            st.session_state.auth = True
            st.rerun()
        else:
            st.error("Usuário ou senha inválidos.")

    st.markdown("</div></div>", unsafe_allow_html=True)
    st.stop()

# Banner topo
header()

# Banner/Logo em cima do menu (SIDEBAR)
if logo_exists():
    show_logo(where="sidebar")
st.sidebar.markdown("---")

# Controle mês a mês global (sidebar)
today = date.today()
default_year = today.year
default_month = today.month

year = st.sidebar.selectbox("Ano", list(range(default_year - 2, default_year + 1)), index=2)
month_name = st.sidebar.selectbox("Mês", MESES_PT, index=default_month - 1)
month = MESES_PT.index(month_name) + 1

start_m, end_m = month_range(year, month)

st.sidebar.caption(f"Período: {start_m.strftime('%d/%m/%Y')} → {(end_m - timedelta(days=1)).strftime('%d/%m/%Y')}")

menu = st.sidebar.radio(
    "Menu",
    ["Agenda", "Robô de Lembretes", "Checkout", "Despesas", "Relatórios (BI)"]
)

# =========================================================
# Agenda
# =========================================================
if menu == "Agenda":
    st.subheader("Novo agendamento")

    with st.form("ag", clear_on_submit=True):
        c1, c2 = st.columns(2)
        cli = c1.text_input("Cliente")
        tel = c2.text_input("WhatsApp")

        serv = st.selectbox("Procedimento", SERVICOS)
        prof = st.selectbox("Profissional", PROFISSIONAIS)

        c3, c4 = st.columns(2)
        dt = c3.date_input("Data", date.today())
        hr = c4.time_input("Horário")

        if st.form_submit_button("Confirmar e enviar WhatsApp"):
            if not cli.strip():
                st.error("Informe o nome do cliente.")
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
            open_whatsapp(link)
            st.success("Agendamento registrado com sucesso.")
            if link:
                st.link_button("Abrir WhatsApp (se não abriu automaticamente)", link)

    st.subheader("Agendamentos do mês selecionado")

    df_ag = pd.read_sql(
        "SELECT * FROM agenda WHERE data >= ? AND data < ? ORDER BY data, hora",
        db,
        params=[date_iso(start_m), date_iso(end_m)]
    )

    if df_ag.empty:
        st.info("Nenhum agendamento neste mês.")
    else:
        st.dataframe(df_ag, use_container_width=True)

        st.markdown("#### ✨ Excluir agendamento")
        st.caption("Selecione pelo ID e confirme para excluir.")

        ids = df_ag["id"].tolist()
        col1, col2, col3 = st.columns([1.2, 2.4, 1.4])

        with col1:
            id_del = st.selectbox("ID", ids)

        with col2:
            row = df_ag[df_ag["id"] == id_del].iloc[0]
            st.write(
                f"📌 **{row['data']} {row['hora']}** — **{row['cliente']}** • {row['servico']} • {row['profissional']}"
            )

        with col3:
            confirm = st.checkbox("Confirmar exclusão", key="confirm_del_agenda")
            if st.button("Excluir", disabled=not confirm):
                db.execute("DELETE FROM agenda WHERE id = ?", (int(id_del),))
                db.commit()
                st.success("Agendamento excluído.")
                st.rerun()

# =========================================================
# Robô de lembretes (hoje)
# =========================================================
elif menu == "Robô de Lembretes":
    st.subheader("Agendamentos de hoje")
    hoje = date.today().isoformat()
    df = pd.read_sql("SELECT * FROM agenda WHERE data = ? ORDER BY hora", db, params=[hoje])

    if df.empty:
        st.info("Nenhum agendamento para hoje.")
    else:
        for _, r in df.iterrows():
            st.write(f"• {r['hora']} — {r['cliente']} — {r['servico']} — {r['profissional']}")
            if st.button("Enviar lembrete", key=f"lem_{r['id']}"):
                link = build_whatsapp_link(r["cliente"], r["telefone"], r["servico"], r["hora"], "lembrete")
                open_whatsapp(link)
                if link:
                    st.link_button("Abrir WhatsApp (fallback)", link)

# =========================================================
# Checkout
# =========================================================
elif menu == "Checkout":
    st.subheader("Finalizar atendimento")

    with st.form("caixa", clear_on_submit=True):
        v_cli = st.text_input("Cliente")
        v_tel = st.text_input("WhatsApp (opcional)")
        v_serv = st.selectbox("Procedimento", SERVICOS)
        v_prof = st.selectbox("Profissional", PROFISSIONAIS)
        v_valor = st.number_input("Valor (R$)", min_value=0.0, format="%.2f")

        if st.form_submit_button("Concluir"):
            if not v_cli.strip():
                st.error("Informe o nome do cliente.")
                st.stop()
            if v_valor <= 0:
                st.error("Informe um valor maior que zero.")
                st.stop()

            comissao = calc_comissao(v_prof, float(v_valor))

            db.execute(
                "INSERT INTO vendas (data, cliente, valor, servico, profissional, comissao) VALUES (?,?,?,?,?,?)",
                (date.today().isoformat(), v_cli.strip(), float(v_valor), v_serv, v_prof, float(comissao))
            )
            db.commit()

            link = build_whatsapp_link(v_cli.strip(), v_tel.strip(), v_serv, "", "agradecimento")
            open_whatsapp(link)

            if v_prof == "Evelyn":
                st.success(f"Venda registrada. 💜 **Comissão Evelyn: R$ {comissao:.2f}**")
            else:
                st.success("Venda registrada (Eunides).")

            if link:
                st.link_button("Abrir WhatsApp (se não abriu automaticamente)", link)

    st.subheader("Vendas do mês selecionado")
    df_vm = pd.read_sql(
        "SELECT * FROM vendas WHERE data >= ? AND data < ? ORDER BY data DESC, id DESC",
        db,
        params=[date_iso(start_m), date_iso(end_m)]
    )
    if df_vm.empty:
        st.info("Nenhuma venda neste mês.")
    else:
        st.dataframe(df_vm, use_container_width=True)

# =========================================================
# Despesas
# =========================================================
elif menu == "Despesas":
    st.subheader("Registrar despesa")

    with st.form("gastos", clear_on_submit=True):
        desc = st.text_input("Descrição")
        val = st.number_input("Valor (R$)", min_value=0.0, format="%.2f")
        if st.form_submit_button("Registrar"):
            if not desc.strip():
                st.error("Informe a descrição.")
                st.stop()
            if val <= 0:
                st.error("Informe um valor maior que zero.")
                st.stop()

            db.execute(
                "INSERT INTO gastos (data, descricao, valor) VALUES (?,?,?)",
                (date.today().isoformat(), desc.strip(), float(val))
            )
            db.commit()
            st.success("Despesa registrada.")

    st.subheader("Despesas do mês selecionado")
    df_gm = pd.read_sql(
        "SELECT * FROM gastos WHERE data >= ? AND data < ? ORDER BY data DESC, id DESC",
        db,
        params=[date_iso(start_m), date_iso(end_m)]
    )
    if df_gm.empty:
        st.info("Nenhuma despesa neste mês.")
    else:
        st.dataframe(df_gm, use_container_width=True)

# =========================================================
# BI (mês a mês)
# =========================================================
elif menu == "Relatórios (BI)":
    st.subheader("Resumo do mês selecionado")

    df_v = pd.read_sql(
        "SELECT * FROM vendas WHERE data >= ? AND data < ?",
        db,
        params=[date_iso(start_m), date_iso(end_m)]
    )
    df_g = pd.read_sql(
        "SELECT * FROM gastos WHERE data >= ? AND data < ?",
        db,
        params=[date_iso(start_m), date_iso(end_m)]
    )

    if not df_v.empty:
        df_v["valor"] = pd.to_numeric(df_v["valor"], errors="coerce").fillna(0.0)
        df_v["comissao"] = pd.to_numeric(df_v["comissao"], errors="coerce").fillna(0.0)
    if not df_g.empty:
        df_g["valor"] = pd.to_numeric(df_g["valor"], errors="coerce").fillna(0.0)

    total_vendas = float(df_v["valor"].sum()) if not df_v.empty else 0.0
    total_comissao = float(df_v["comissao"].sum()) if not df_v.empty else 0.0
    total_gastos = float(df_g["valor"].sum()) if not df_g.empty else 0.0

    lucro = total_vendas - total_comissao - total_gastos

    # Comissão Evelyn (100% do que ela fez)
    if not df_v.empty:
        df_eve = df_v[df_v["profissional"].str.lower() == "evelyn"]
        comissao_evelyn = float(df_eve["comissao"].sum()) if not df_eve.empty else 0.0
        vendas_evelyn = float(df_eve["valor"].sum()) if not df_eve.empty else 0.0
    else:
        comissao_evelyn = 0.0
        vendas_evelyn = 0.0

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Faturamento total", f"R$ {total_vendas:.2f}")
    c2.metric("Vendas Evelyn", f"R$ {vendas_evelyn:.2f}")
    c3.metric("Comissão Evelyn", f"R$ {comissao_evelyn:.2f}")
    c4.metric("Lucro do salão", f"R$ {lucro:.2f}")

    st.subheader("Detalhe por profissional")
    if df_v.empty:
        st.info("Sem vendas registradas neste mês.")
    else:
        resumo = (
            df_v.groupby("profissional", as_index=False)
               .agg(vendas=("valor", "sum"), comissao=("comissao", "sum"))
        )
        st.dataframe(resumo, use_container_width=True)

        fig = px.bar(
            resumo,
            x="profissional",
            y="vendas",
            title="Faturamento por profissional (mês)"
        )
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Últimas vendas do mês")
    if df_v.empty:
        st.info("Sem vendas registradas.")
    else:
        st.dataframe(
            df_v.sort_values(["data", "id"], ascending=[False, False]).head(25),
            use_container_width=True
        )
