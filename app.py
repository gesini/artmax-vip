import sqlite3
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
import urllib.parse
import plotly.express as px
from datetime import date

# =========================================================
# CONFIG
# =========================================================
APP_NAME = "Artmax Cabeleleiros"
DB_PATH = "artmax.db"

st.set_page_config(page_title=APP_NAME, layout="wide", page_icon="💜")

# =========================================================
# PALETA (roxo + dourado + preto + branco)
# =========================================================
C_BG = "#0B0B10"
C_TEXT = "rgba(255,255,255,0.92)"
C_MUTED = "rgba(255,255,255,0.72)"
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
# UI (feminina / linda / premium)
# =========================================================
def apply_ui():
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=Inter:wght@400;500;600&display=swap');

    .stApp {{
        background:
          radial-gradient(circle at 20% 0%, rgba(142,45,226,0.28), rgba(11,11,16,0.92) 40%),
          radial-gradient(circle at 80% 30%, rgba(212,175,55,0.10), rgba(11,11,16,0.0) 45%),
          {C_BG};
        color: {C_TEXT};
        font-family: 'Inter', sans-serif;
    }}

    /* Header premium */
    .app-header {{
        background: linear-gradient(135deg, rgba(74,0,224,0.55), rgba(142,45,226,0.35));
        border: 1px solid {C_GOLD_SOFT};
        padding: 18px 22px;
        border-radius: 20px;
        margin-bottom: 18px;
        box-shadow: 0 16px 40px rgba(0,0,0,0.45);
        position: relative;
        overflow: hidden;
    }}
    .app-header:before {{
        content: "";
        position: absolute;
        inset: -50%;
        background: radial-gradient(circle, rgba(212,175,55,0.10), rgba(255,255,255,0.0) 55%);
        transform: rotate(8deg);
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
        text-shadow: 0 8px 22px rgba(0,0,0,0.45);
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
        box-shadow: 0 0 18px rgba(212,175,55,0.35);
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

    /* Tabelas */
    div[data-testid="stDataFrame"] {{
        background: {C_SURFACE_2} !important;
        border: 1px solid rgba(255,255,255,0.10) !important;
        border-radius: 18px !important;
        padding: 10px !important;
        backdrop-filter: blur(10px);
    }}

    /* FIX do seu print: garante contraste do st.metric */
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

    /* Buttons dourado */
    .stButton>button {{
        background: linear-gradient(90deg, {C_GOLD}, #B8860B) !important;
        color: #0B0B10 !important;
        border: none !important;
        border-radius: 14px;
        height: 48px;
        font-weight: 700;
        transition: 0.15s;
        text-transform: none;
    }}
    .stButton>button:hover {{
        transform: translateY(-1px);
        box-shadow: 0 12px 28px rgba(212,175,55,0.22);
    }}

    /* Sidebar elegante */
    section[data-testid="stSidebar"] {{
        background: linear-gradient(180deg, rgba(74,0,224,0.20), rgba(11,11,16,0.96)) !important;
        border-right: 1px solid rgba(212,175,55,0.16);
    }}
    section[data-testid="stSidebar"] * {{
        color: {C_TEXT} !important;
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

# =========================================================
# REGRA: comissão só da Evelyn (100% do que ela fizer)
# =========================================================
def calc_comissao(profissional: str, valor_venda: float) -> float:
    if profissional.strip().lower() == "evelyn":
        return float(valor_venda)
    return 0.0

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

if not st.session_state.auth:
    header()
    st.caption("Acesso restrito.")
    u = st.text_input("Usuário")
    s = st.text_input("Senha", type="password")
    if st.button("Entrar"):
        if u.strip().lower() == "artmax" and s.strip() == "gesini123":
            st.session_state.auth = True
            st.rerun()
        else:
            st.error("Credenciais inválidas.")
    st.stop()

header()

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

    st.subheader("Próximos agendamentos")
    df_next = pd.read_sql(
        "SELECT * FROM agenda WHERE data >= ? ORDER BY data, hora LIMIT 30",
        db,
        params=[date.today().isoformat()]
    )
    if df_next.empty:
        st.info("Nenhum agendamento futuro.")
    else:
        st.dataframe(df_next, use_container_width=True)

# =========================================================
# Robô
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

    st.subheader("Últimas despesas")
    df_g = pd.read_sql("SELECT * FROM gastos ORDER BY data DESC, id DESC LIMIT 20", db)
    if df_g.empty:
        st.info("Sem despesas cadastradas.")
    else:
        st.dataframe(df_g, use_container_width=True)

# =========================================================
# BI
# =========================================================
elif menu == "Relatórios (BI)":
    st.subheader("Resumo financeiro")

    df_v = pd.read_sql("SELECT * FROM vendas", db)
    df_g = pd.read_sql("SELECT * FROM gastos", db)

    if not df_v.empty:
        df_v["valor"] = pd.to_numeric(df_v["valor"], errors="coerce").fillna(0.0)
        df_v["comissao"] = pd.to_numeric(df_v["comissao"], errors="coerce").fillna(0.0)
    if not df_g.empty:
        df_g["valor"] = pd.to_numeric(df_g["valor"], errors="coerce").fillna(0.0)

    total_vendas = float(df_v["valor"].sum()) if not df_v.empty else 0.0
    total_comissao = float(df_v["comissao"].sum()) if not df_v.empty else 0.0
    total_gastos = float(df_g["valor"].sum()) if not df_g.empty else 0.0

    lucro = total_vendas - total_comissao - total_gastos

    # Comissão Evelyn (já é 100% das vendas dela)
    if not df_v.empty:
        df_eve = df_v[df_v["profissional"].str.lower() == "evelyn"]
        comissao_evelyn = float(df_eve["comissao"].sum()) if not df_eve.empty else 0.0
    else:
        comissao_evelyn = 0.0

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Faturamento total", f"R$ {total_vendas:.2f}")
    c2.metric("Comissão Evelyn", f"R$ {comissao_evelyn:.2f}")
    c3.metric("Despesas", f"R$ {total_gastos:.2f}")
    c4.metric("Lucro do salão", f"R$ {lucro:.2f}")

    st.subheader("Detalhe por profissional")
    if df_v.empty:
        st.info("Sem vendas registradas.")
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
            title="Faturamento por profissional"
        )
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Últimas vendas")
    if df_v.empty:
        st.info("Sem vendas registradas.")
    else:
        st.dataframe(
            df_v.sort_values(["data", "id"], ascending=[False, False]).head(25),
            use_container_width=True
        )
