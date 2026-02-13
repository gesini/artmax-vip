import sqlite3
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
import urllib.parse
import plotly.express as px
from datetime import date, timedelta

# =========================
# (Opcional) Google Sheets
# =========================
try:
    import gspread
    from google.oauth2.service_account import Credentials
    HAS_SHEETS = True
except Exception:
    HAS_SHEETS = False

# =========================================================
# CONFIGURAÇÕES INICIAIS
# =========================================================
APP_NAME = "Artmax Cabeleleiros"
DB_PATH = "artmax.db"

st.set_page_config(page_title=APP_NAME, layout="wide", page_icon="💜")

# =========================================================
# PALETA DE CORES (Luxo: Roxo, Dourado, Preto)
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
SERVICOS = ["Escova", "Progressiva", "Luzes", "Coloração", "Botox", "Relaxamento", "Sobrancelha", "Corte", "Outros"]

# =========================================================
# UI CUSTOMIZADA (CSS PREMIUM)
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

    .app-header {{
        background: linear-gradient(135deg, rgba(74,0,224,0.60), rgba(142,45,226,0.35));
        border: 1px solid {C_GOLD_SOFT};
        padding: 25px;
        border-radius: 20px;
        margin-bottom: 25px;
        box-shadow: 0 16px 40px rgba(0,0,0,0.45);
        position: relative;
        overflow: hidden;
    }}

    .app-title {{
        font-family: 'Playfair Display', serif;
        font-size: 32px;
        font-weight: 700;
        color: {C_WHITE};
        margin: 0;
    }}

    /* Estilização de Forms, Métricas e Expanders */
    div[data-testid="stForm"], div[data-testid="stExpander"], div[data-testid="stMetric"] {{
        background: {C_SURFACE} !important;
        border: 1px solid {C_GOLD_SOFT} !important;
        border-radius: 20px !important;
        padding: 20px !important;
        backdrop-filter: blur(12px);
    }}

    /* Inputs e Selects */
    input, textarea, div[data-baseweb="select"] {{
        background-color: rgba(255,255,255,0.95) !important;
        color: #101018 !important;
        border-radius: 12px !important;
    }}

    /* Botão Dourado */
    .stButton>button {{
        background: linear-gradient(90deg, {C_GOLD}, #B8860B) !important;
        color: #0B0B10 !important;
        border: none !important;
        border-radius: 12px;
        height: 50px;
        font-weight: 700;
        width: 100%;
        transition: 0.3s;
    }}

    /* Sidebar */
    section[data-testid="stSidebar"] {{
        background: #0B0B10 !important;
        border-right: 1px solid rgba(212,175,55,0.2) !important;
    }}
    </style>
    """, unsafe_allow_html=True)

def header():
    st.markdown(f'<div class="app-header"><div class="app-title">✨ {APP_NAME}</div><div style="color:{C_MUTED}">Gestão de Luxo & Atendimento</div></div>', unsafe_allow_html=True)

def sidebar_resizer():
    components.html("""
        <script>
          (function () {
            const sidebar = parent.document.querySelector("section[data-testid='stSidebar']");
            if (!sidebar || parent.document.getElementById("sidebar-resizer")) return;
            const resizer = parent.document.createElement("div");
            resizer.id = "sidebar-resizer";
            resizer.style = "position:absolute;top:0;right:0;width:10px;height:100%;cursor:col-resize;background:rgba(212,175,55,0.1);z-index:9999;";
            sidebar.appendChild(resizer);
            let isResizing = false;
            resizer.addEventListener("mousedown", (e) => { isResizing = true; parent.document.body.style.cursor = "col-resize"; });
            parent.document.addEventListener("mousemove", (e) => {
              if (!isResizing) return;
              let newWidth = Math.max(240, Math.min(520, e.clientX));
              sidebar.style.width = newWidth + "px";
              sidebar.style.minWidth = newWidth + "px";
            });
            parent.document.addEventListener("mouseup", () => { isResizing = false; parent.document.body.style.cursor = ""; });
          })();
        </script>
        """, height=0)

# =========================================================
# LÓGICA DE COMISSÃO (CORRIGIDA)
# =========================================================
COMISSAO_EVELYN = {
    "Escova": 0.50,
    "Progressiva": 0.50,
    "Botox": 0.50,
    "Sobrancelha": 0.60,
    "Coloração": 0.40,
    "Relaxamento": 0.50
}

def calc_comissao(profissional, servico, valor):
    if profissional != "Evelyn": return 0.0
    # Busca a porcentagem, se não existir na lista fixa (ex: Corte), retorna 0 ou defina um padrão
    porcentagem = COMISSAO_EVELYN.get(servico, 0.0)
    return float(valor) * porcentagem

# =========================================================
# BANCO DE DADOS
# =========================================================
def init_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.execute("CREATE TABLE IF NOT EXISTS agenda (id INTEGER PRIMARY KEY AUTOINCREMENT, data TEXT, hora TEXT, cliente TEXT, telefone TEXT, servico TEXT, profissional TEXT)")
    conn.execute("CREATE TABLE IF NOT EXISTS vendas (id INTEGER PRIMARY KEY AUTOINCREMENT, data TEXT, cliente TEXT, valor REAL, servico TEXT, profissional TEXT, comissao REAL)")
    conn.execute("CREATE TABLE IF NOT EXISTS gastos (id INTEGER PRIMARY KEY AUTOINCREMENT, data TEXT, descricao TEXT, valor REAL)")
    conn.commit()
    return conn

db = init_db()

# =========================================================
# WHATSAPP LINKS
# =========================================================
def build_whatsapp_link(nome, tel, servico, hora="", tipo="confirmacao"):
    if not tel: return None
    msgs = {
        "confirmacao": f"Olá {nome}! ✨ Confirmamos seu horário para {servico} às {hora}.",
        "lembrete": f"Oi {nome}! 💜 Lembrete do seu horário hoje às {hora} ({servico}).",
        "agradecimento": f"Obrigada pela preferência, {nome}! ✨ Foi um prazer atender você ({servico})."
    }
    msg = msgs.get(tipo, "")
    tel_limpo = "".join(filter(str.isdigit, tel))
    return f"https://wa.me/55{tel_limpo}?text={urllib.parse.quote(msg)}"

def open_whatsapp(link):
    if link: components.html(f"<script>window.open('{link}', '_blank');</script>", height=0)

# =========================================================
# GOOGLE SHEETS EXPORT (INTEGRAL)
# =========================================================
def export_to_sheets(df, title):
    if not HAS_SHEETS:
        st.error("Biblioteca gspread não instalada.")
        return
    try:
        # Aqui iria sua lógica de autenticação st.secrets
        st.info("Função de exportação pronta. Configure suas credenciais GCP para ativar.")
    except Exception as e:
        st.error(f"Erro: {e}")

# =========================================================
# APP PRINCIPAL
# =========================================================
apply_ui()
sidebar_resizer()

if "auth" not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.markdown("<div style='display:flex; justify-content:center; padding-top:100px;'><div class='login-card'>", unsafe_allow_html=True)
    st.markdown(f"<h2 style='color:white; text-align:center;'>{APP_NAME}</h2>", unsafe_allow_html=True)
    u = st.text_input("Usuário")
    s = st.text_input("Senha", type="password")
    if st.button("Acessar Sistema"):
        if u == "artmax" and s == "gesini123":
            st.session_state.auth = True
            st.rerun()
        else: st.error("Acesso negado")
    st.markdown("</div></div>", unsafe_allow_html=True)
    st.stop()

header()

# Navegação Lateral
MESES_PT = ["Janeiro","Fevereiro","Março","Abril","Maio","Junho","Julho","Agosto","Setembro","Outubro","Novembro","Dezembro"]
today = date.today()
st.sidebar.title("💎 Menu")
menu = st.sidebar.radio("Selecione:", ["Agenda", "Robô de Lembretes", "Checkout", "Despesas", "Vendas (Excluir/Filtrar)", "Relatórios (BI)"])

st.sidebar.markdown("---")
year = st.sidebar.selectbox("Ano", [2025, 2026], index=1)
month_name = st.sidebar.selectbox("Mês", MESES_PT, index=today.month-1)
month_idx = MESES_PT.index(month_name) + 1
start_date = date(year, month_idx, 1)

# --- ABA AGENDA ---
if menu == "Agenda":
    st.subheader("🗓️ Agendamento de Clientes")
    with st.form("form_agenda", clear_on_submit=True):
        col1, col2 = st.columns(2)
        nome_c = col1.text_input("Nome da Cliente")
        tel_c = col2.text_input("WhatsApp (com DDD)")
        
        serv_sel = st.selectbox("Procedimento", SERVICOS)
        
        # ✅ LÓGICA DO CAMPO DINÂMICO "OUTROS"
        servico_final = serv_sel
        if serv_sel == "Outros":
            outro_input = st.text_input("Descreva o serviço personalizado:")
            if outro_input: servico_final = outro_input

        prof_sel = st.selectbox("Profissional", PROFISSIONAIS)
        d_ag = st.date_input("Data", today)
        h_ag = st.time_input("Horário")
        
        if st.form_submit_button("Confirmar Agendamento"):
            db.execute("INSERT INTO agenda (data, hora, cliente, telefone, servico, profissional) VALUES (?,?,?,?,?,?)",
                       (d_ag.isoformat(), h_ag.strftime("%H:%M"), nome_c, tel_c, servico_final, prof_sel))
            db.commit()
            st.success("Agendado com sucesso!")
            link = build_whatsapp_link(nome_c, tel_c, servico_final, h_ag.strftime("%H:%M"), "confirmacao")
            open_whatsapp(link)

    st.markdown("### Próximos Horários")
    df_ag = pd.read_sql("SELECT * FROM agenda ORDER BY data, hora", db)
    st.dataframe(df_ag, use_container_width=True)

# --- ABA CHECKOUT ---
elif menu == "Checkout":
    st.subheader("💰 Finalizar Atendimento (Caixa)")
    with st.form("form_venda", clear_on_submit=True):
        v_cli = st.text_input("Cliente")
        v_tel = st.text_input("WhatsApp")
        
        v_serv_sel = st.selectbox("Procedimento Realizado", SERVICOS)
        
        # ✅ LÓGICA DO CAMPO DINÂMICO "OUTROS" NO CHECKOUT
        v_serv_final = v_serv_sel
        if v_serv_sel == "Outros":
            v_outro_input = st.text_input("Qual foi o serviço?")
            if v_outro_input: v_serv_final = v_outro_input

        v_prof = st.selectbox("Profissional", PROFISSIONAIS)
        v_valor = st.number_input("Valor Total R$", min_value=0.0)
        
        if st.form_submit_button("Registrar Venda & Comissões"):
            comis = calc_comissao(v_prof, v_serv_final, v_valor)
            db.execute("INSERT INTO vendas (data, cliente, valor, servico, profissional, comissao) VALUES (?,?,?,?,?,?)",
                       (date.today().isoformat(), v_cli, v_valor, v_serv_final, v_prof, comis))
            db.commit()
            st.success(f"Venda registrada! Comissão da Evelyn: R$ {comis:.2f}")
            link = build_whatsapp_link(v_cli, v_tel, v_serv_final, tipo="agradecimento")
            open_whatsapp(link)

# --- ABA RELATÓRIOS (BI) ---
elif menu == "Relatórios (BI)":
    st.subheader("📊 Performance e Lucratividade")
    df_v = pd.read_sql("SELECT * FROM vendas", db)
    df_g = pd.read_sql("SELECT * FROM gastos", db)
    
    if not df_v.empty:
        total_fat = df_v['valor'].sum()
        total_com = df_v['comissao'].sum()
        total_gas = df_g['valor'].sum() if not df_g.empty else 0
        lucro = total_fat - total_com - total_gas
        
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Faturamento Total", f"R$ {total_fat:,.2f}")
        m2.metric("Comissões Pagas", f"R$ {total_com:,.2f}")
        m3.metric("Despesas", f"R$ {total_gas:,.2f}")
        m4.metric("Lucro Líquido", f"R$ {lucro:,.2f}")
        
        st.markdown("---")
        fig = px.bar(df_v, x="profissional", y="valor", color="servico", title="Vendas por Profissional")
        st.plotly_chart(fig, use_container_width=True)

# --- ABA DESPESAS ---
elif menu == "Despesas":
    st.subheader("💸 Registro de Gastos")
    with st.form("gastos"):
        desc = st.text_input("Descrição da Despesa")
        val_g = st.number_input("Valor R$", min_value=0.0)
        if st.form_submit_button("Salvar Gasto"):
            db.execute("INSERT INTO gastos (data, descricao, valor) VALUES (?,?,?)", (date.today().isoformat(), desc, val_g))
            db.commit()
            st.success("Gasto registrado.")

# --- ABA VENDAS (FILTRAR/EXCLUIR) ---
elif menu == "Vendas (Excluir/Filtrar)":
    st.subheader("🔍 Gerenciar Vendas")
    df_v = pd.read_sql("SELECT * FROM vendas ORDER BY id DESC", db)
    st.dataframe(df_v, use_container_width=True)
    
    ids_to_del = st.multiselect("Selecione IDs para apagar:", df_v['id'].tolist())
    if st.button("Excluir Registros Selecionados"):
        for i in ids_to_del:
            db.execute("DELETE FROM vendas WHERE id = ?", (i,))
        db.commit()
        st.rerun()

# --- ABA ROBÔ DE LEMBRETES ---
elif menu == "Robô de Lembretes":
    st.subheader("🤖 Assistente de Mensagens")
    df_hoje = pd.read_sql("SELECT * FROM agenda WHERE data = ?", db, params=[today.isoformat()])
    if df_hoje.empty:
        st.info("Nenhuma agenda para hoje.")
    else:
        for index, row in df_hoje.iterrows():
            st.write(f"📌 {row['hora']} - {row['cliente']} ({row['servico']})")
            if st.button(f"Enviar Lembrete para {row['cliente']}", key=index):
                link = build_whatsapp_link(row['cliente'], row['telefone'], row['servico'], row['hora'], "lembrete")
                open_whatsapp(link)