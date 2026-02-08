# =========================================================
# config.py
# =========================================================
from dataclasses import dataclass
from typing import List
import os
from pathlib import Path

BASE_DIR = Path(__file__).parent
DB_PATH = BASE_DIR / "artmax.db"

APP_NAME = "Artmax Cabeleleiros"
APP_ICON = "👑"

SECRET_KEY = os.getenv("SECRET_KEY", "change-me-in-production")
SESSION_TIMEOUT_MINUTES = 60

@dataclass(frozen=True)
class ColorPalette:
    BG: str = "#0B0B10"
    SURFACE: str = "rgba(255,255,255,0.05)"
    BORDER: str = "rgba(212,175,55,0.22)"
    TEXT: str = "rgba(255,255,255,0.92)"
    MUTED: str = "rgba(255,255,255,0.70)"
    PURPLE_1: str = "#4A00E0"
    PURPLE_2: str = "#8E2DE2"
    GOLD: str = "#D4AF37"
    WHITE: str = "#FFFFFF"

COLORS = ColorPalette()

PROFISSIONAIS: List[str] = ["Eunides", "Evelyn"]
SERVICOS: List[str] = [
    "Escova", "Progressiva", "Luzes",
    "Coloração", "Botox", "Corte", "Outros"
]

REPASSE_RULES = {
    "evelyn": 1.0,
    "eunides": 0.0
}

WHATSAPP_MESSAGES = {
    "confirmacao": "Olá {nome}! Confirmamos seu horário para {servico} às {hora}.",
    "lembrete": "Olá {nome}! Lembrete do seu horário hoje às {hora} ({servico}).",
    "agradecimento": "Obrigada pela preferência, {nome}! Foi um prazer atender você ({servico})."
}

MIN_PHONE_DIGITS = 10
MAX_PHONE_DIGITS = 11
MIN_VALUE = 0.01
MAX_VALUE = 10000.0


# =========================================================
# database.py
# =========================================================
import sqlite3
import threading
from contextlib import contextmanager
from typing import List, Dict, Any

class DatabaseManager:
    _local = threading.local()
    _lock = threading.Lock()

    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
        self._init_db()

    def _get_conn(self):
        if not hasattr(self._local, "conn"):
            self._local.conn = sqlite3.connect(
                self.db_path, check_same_thread=False
            )
            self._local.conn.row_factory = sqlite3.Row
        return self._local.conn

    @contextmanager
    def cursor(self):
        conn = self._get_conn()
        cur = conn.cursor()
        try:
            yield cur
            conn.commit()
        except:
            conn.rollback()
            raise
        finally:
            cur.close()

    def _init_db(self):
        with self._lock, self.cursor() as c:
            c.execute("""
            CREATE TABLE IF NOT EXISTS agenda (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                data TEXT,
                hora TEXT,
                cliente TEXT,
                telefone TEXT,
                servico TEXT,
                profissional TEXT,
                status TEXT DEFAULT 'agendado'
            )""")

            c.execute("""
            CREATE TABLE IF NOT EXISTS vendas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                data TEXT,
                cliente TEXT,
                valor REAL,
                servico TEXT,
                profissional TEXT,
                repasse REAL
            )""")

            c.execute("""
            CREATE TABLE IF NOT EXISTS gastos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                data TEXT,
                descricao TEXT,
                valor REAL,
                categoria TEXT
            )""")

    def insert_agendamento(self, data, hora, cliente, telefone, servico, profissional):
        with self.cursor() as c:
            c.execute("""
            INSERT INTO agenda VALUES (NULL,?,?,?,?,?, 'agendado')
            """, (data, hora, cliente, telefone, servico, profissional))
            return c.lastrowid

    def get_agendamentos_futuros(self):
        with self.cursor() as c:
            c.execute("SELECT * FROM agenda ORDER BY data, hora")
            return [dict(r) for r in c.fetchall()]

    def get_agendamentos_dia(self, data):
        with self.cursor() as c:
            c.execute("SELECT * FROM agenda WHERE data=?", (data,))
            return [dict(r) for r in c.fetchall()]

    def insert_venda(self, data, cliente, valor, servico, profissional, repasse):
        with self.cursor() as c:
            c.execute("""
            INSERT INTO vendas VALUES (NULL,?,?,?,?,?,?)
            """, (data, cliente, valor, servico, profissional, repasse))
            return c.lastrowid

    def get_all_vendas(self):
        with self.cursor() as c:
            c.execute("SELECT * FROM vendas")
            return [dict(r) for r in c.fetchall()]

    def get_vendas_por_profissional(self):
        with self.cursor() as c:
            c.execute("""
            SELECT profissional, SUM(valor) vendas, SUM(repasse) repasse
            FROM vendas GROUP BY profissional
            """)
            return [dict(r) for r in c.fetchall()]

    def insert_gasto(self, data, descricao, valor, categoria):
        with self.cursor() as c:
            c.execute("""
            INSERT INTO gastos VALUES (NULL,?,?,?,?)
            """, (data, descricao, valor, categoria))
            return c.lastrowid

    def get_gastos_recentes(self):
        with self.cursor() as c:
            c.execute("SELECT * FROM gastos ORDER BY data DESC")
            return [dict(r) for r in c.fetchall()]


# =========================================================
# models.py
# =========================================================
from dataclasses import dataclass
from datetime import date
import re

class ValidationError(Exception):
    pass

@dataclass
class Agendamento:
    cliente: str
    telefone: str
    servico: str
    profissional: str
    data: date
    hora: str

    def __post_init__(self):
        if len(self.cliente.strip()) < 2:
            raise ValidationError("Cliente inválido")
        digits = re.sub(r"\D", "", self.telefone)
        if not (MIN_PHONE_DIGITS <= len(digits) <= MAX_PHONE_DIGITS):
            raise ValidationError("Telefone inválido")


@dataclass
class Venda:
    cliente: str
    valor: float
    servico: str
    profissional: str
    data: date
    repasse: float

    def __post_init__(self):
        if not (MIN_VALUE <= self.valor <= MAX_VALUE):
            raise ValidationError("Valor inválido")


@dataclass
class Gasto:
    descricao: str
    valor: float
    data: date
    categoria: str

    def __post_init__(self):
        if len(self.descricao.strip()) < 3:
            raise ValidationError("Descrição inválida")


# =========================================================
# services.py
# =========================================================
import urllib.parse
from datetime import date

class BusinessService:
    def __init__(self, db: DatabaseManager):
        self.db = db

    def calcular_repasse(self, profissional, valor):
        return round(valor * REPASSE_RULES.get(profissional.lower(), 0), 2)

    def criar_agendamento(self, cliente, telefone, servico, profissional, data, hora):
        Agendamento(cliente, telefone, servico, profissional, data, hora)
        ag_id = self.db.insert_agendamento(
            data.isoformat(), hora, cliente, telefone, servico, profissional
        )
        msg = WHATSAPP_MESSAGES["confirmacao"].format(
            nome=cliente, servico=servico, hora=hora
        )
        link = f"https://wa.me/55{''.join(filter(str.isdigit, telefone))}?text={urllib.parse.quote(msg)}"
        return ag_id, link

    def finalizar_venda(self, cliente, valor, servico, profissional, telefone=None):
        repasse = self.calcular_repasse(profissional, valor)
        Venda(cliente, valor, servico, profissional, date.today(), repasse)
        venda_id = self.db.insert_venda(
            date.today().isoformat(), cliente, valor, servico, profissional, repasse
        )
        link = None
        if telefone:
            msg = WHATSAPP_MESSAGES["agradecimento"].format(
                nome=cliente, servico=servico, hora=""
            )
            link = f"https://wa.me/55{''.join(filter(str.isdigit, telefone))}?text={urllib.parse.quote(msg)}"
        return venda_id, repasse, link

    def registrar_gasto(self, descricao, valor, categoria):
        Gasto(descricao, valor, date.today(), categoria)
        return self.db.insert_gasto(
            date.today().isoformat(), descricao, valor, categoria
        )

    def calcular_metricas_financeiras(self):
        vendas = self.db.get_all_vendas()
        gastos = self.db.get_gastos_recentes()
        total_vendas = sum(v["valor"] for v in vendas)
        total_repasse = sum(v["repasse"] for v in vendas)
        total_gastos = sum(g["valor"] for g in gastos)
        return {
            "total_vendas": total_vendas,
            "total_repasse": total_repasse,
            "total_gastos": total_gastos,
            "lucro": total_vendas - total_repasse - total_gastos
        }


# =========================================================
# requirements.txt
# =========================================================
"""
streamlit>=1.32.0
pandas>=2.0.0
plotly>=5.18.0
"""
