"""
╔══════════════════════════════════════════════════════════════════════════════╗
║   DATABASE — Sistema de Atendimentos Samsung SMB                            ║
║   MySQL (Workbench) | Atendimentos + Pagamentos + Vendedores                ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import os

# Carrega .env apenas se disponível (ambiente local de desenvolvimento)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


import mysql.connector
from mysql.connector import pooling, IntegrityError
from datetime import datetime

# ─────────────────────────────────────────────────────────────────────────────
# CONFIGURAÇÃO DA CONEXÃO (via variáveis de ambiente ou st.secrets)
# ─────────────────────────────────────────────────────────────────────────────

def _mysql_config() -> dict:
    """Lê as credenciais MySQL do ambiente (ou st.secrets, se disponível)."""
    try:
        import streamlit as st
        secrets = st.secrets
        return {
            "host":     secrets.get("MYSQL_HOST",     os.environ.get("MYSQL_HOST",     "127.0.0.1")),
            "port":     int(secrets.get("MYSQL_PORT", os.environ.get("MYSQL_PORT",     "3306"))),
            "user":     secrets.get("MYSQL_USER",     os.environ.get("MYSQL_USER",     "root")),
            "password": secrets.get("MYSQL_PASSWORD", os.environ.get("MYSQL_PASSWORD", "Abn@rum12")),
            "database": secrets.get("MYSQL_DATABASE", os.environ.get("MYSQL_DATABASE", "samsung_smb")),
        }
    except Exception:
        return {
            "host":     os.environ.get("MYSQL_HOST",     "127.0.0.1"),
            "port":     int(os.environ.get("MYSQL_PORT", "3306")),
            "user":     os.environ.get("MYSQL_USER",     "root"),
            "password": os.environ.get("MYSQL_PASSWORD", ""),
            "database": os.environ.get("MYSQL_DATABASE", "samsung_smb"),
        }


# Pool simples reutilizável (tamanho 5 — suficiente para Streamlit local/cloud)
_pool: pooling.MySQLConnectionPool | None = None


def _get_pool() -> pooling.MySQLConnectionPool:
    global _pool
    if _pool is None:
        cfg = _mysql_config()
        _pool = pooling.MySQLConnectionPool(
            pool_name="smb_pool",
            pool_size=5,
            **cfg,
        )
    return _pool


def get_conn():
    """Retorna uma conexão do pool."""
    return _get_pool().get_connection()


# ─────────────────────────────────────────────────────────────────────────────
# INICIALIZAÇÃO DO BANCO
# ─────────────────────────────────────────────────────────────────────────────

def init_db():
    conn = get_conn()
    cur  = conn.cursor()

    # ── Tabela atendimentos ──────────────────────────────────────────────────
    cur.execute("""
        CREATE TABLE IF NOT EXISTS atendimentos (
            id                  INT           AUTO_INCREMENT PRIMARY KEY,
            atendente           VARCHAR(150)  NOT NULL,
            data_atendimento    VARCHAR(20)   NOT NULL,
            numero_pedido       VARCHAR(100)  NOT NULL UNIQUE,
            nome_cliente        VARCHAR(200)  NOT NULL,
            valor_pedido        DOUBLE        NOT NULL DEFAULT 0.0,
            arquivo_comprovante VARCHAR(300)  DEFAULT '',
            data_hora_registro  VARCHAR(30)   DEFAULT ''
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """)

    # ── Tabela pagamentos ────────────────────────────────────────────────────
    cur.execute("""
        CREATE TABLE IF NOT EXISTS pagamentos (
            id                  INT           AUTO_INCREMENT PRIMARY KEY,
            numero_os           VARCHAR(100)  NOT NULL,
            atendente           VARCHAR(150)  DEFAULT '',
            data_pagamento      VARCHAR(20)   DEFAULT '',
            nome_cliente        VARCHAR(200)  DEFAULT '',
            valor_produto       DOUBLE        DEFAULT 0.0,
            valor_entrada       DOUBLE        DEFAULT 0.0,
            valor_saldo         DOUBLE        DEFAULT 0.0,
            tipo_pagamento      VARCHAR(80)   DEFAULT '',
            arquivo_comprovante VARCHAR(300)  DEFAULT '',
            data_hora_registro  VARCHAR(30)   DEFAULT ''
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """)

    # ── Tabela vendedores ────────────────────────────────────────────────────
    cur.execute("""
        CREATE TABLE IF NOT EXISTS vendedores (
            id         INT          AUTO_INCREMENT PRIMARY KEY,
            nome       VARCHAR(150) NOT NULL UNIQUE,
            criado_em  VARCHAR(30)  DEFAULT ''
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """)

    conn.commit()
    cur.close()
    conn.close()


# Inicializa ao importar
init_db()


# ═══════════════════════════════════════════════════════════════════════════════
# ATENDIMENTOS
# ═══════════════════════════════════════════════════════════════════════════════

def salvar_atendimento(dados: dict):
    conn = get_conn()
    cur  = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO atendimentos
                (atendente, data_atendimento, numero_pedido, nome_cliente,
                 valor_pedido, arquivo_comprovante, data_hora_registro)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            dados["atendente"],
            dados["data_atendimento"],
            dados["numero_pedido"],
            dados["nome_cliente"],
            dados["valor_pedido"],
            dados.get("arquivo_comprovante", ""),
            dados.get("data_hora_registro", datetime.now().strftime("%d/%m/%Y %H:%M:%S")),
        ))
        conn.commit()
    except IntegrityError:
        raise ValueError(f"Número de pedido '{dados['numero_pedido']}' já cadastrado.")
    finally:
        cur.close()
        conn.close()


def carregar_atendimentos() -> list[dict]:
    conn = get_conn()
    cur  = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM atendimentos ORDER BY id DESC")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


def contar_atendimentos() -> int:
    conn = get_conn()
    cur  = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM atendimentos")
    count = cur.fetchone()[0]
    cur.close()
    conn.close()
    return count


def obter_valor_total() -> float:
    conn = get_conn()
    cur  = conn.cursor()
    cur.execute("SELECT COALESCE(SUM(valor_pedido), 0) FROM atendimentos")
    total = cur.fetchone()[0]
    cur.close()
    conn.close()
    return float(total)


def atualizar_atendimento(id_: int, dados: dict):
    conn = get_conn()
    cur  = conn.cursor()
    cur.execute("""
        UPDATE atendimentos
        SET atendente=%s, data_atendimento=%s, numero_pedido=%s,
            nome_cliente=%s, valor_pedido=%s
        WHERE id=%s
    """, (
        dados["atendente"],
        dados["data_atendimento"],
        dados["numero_pedido"],
        dados["nome_cliente"],
        dados["valor_pedido"],
        id_,
    ))
    conn.commit()
    cur.close()
    conn.close()


def limpar_todos_dados():
    conn = get_conn()
    cur  = conn.cursor()
    cur.execute("DELETE FROM atendimentos")
    conn.commit()
    cur.close()
    conn.close()


def estatisticas_por_atendente() -> list[dict]:
    conn = get_conn()
    cur  = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT
            atendente,
            COUNT(*)          AS total_atendimentos,
            SUM(valor_pedido) AS valor_total,
            AVG(valor_pedido) AS valor_medio
        FROM atendimentos
        GROUP BY atendente
        ORDER BY valor_total DESC
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


def estatisticas_por_periodo() -> list[dict]:
    conn = get_conn()
    cur  = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT
            data_atendimento       AS periodo,
            COUNT(*)               AS total,
            SUM(valor_pedido)      AS valor_total
        FROM atendimentos
        GROUP BY data_atendimento
        ORDER BY data_atendimento DESC
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


def evolucao_por_vendedor() -> list[dict]:
    conn = get_conn()
    cur  = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT
            atendente,
            data_atendimento AS data,
            SUM(valor_pedido) AS valor_total
        FROM atendimentos
        GROUP BY atendente, data_atendimento
        ORDER BY data_atendimento
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


# ═══════════════════════════════════════════════════════════════════════════════
# PAGAMENTOS
# ═══════════════════════════════════════════════════════════════════════════════

def salvar_pagamento(dados: dict):
    conn = get_conn()
    cur  = conn.cursor()
    cur.execute("""
        INSERT INTO pagamentos
            (numero_os, atendente, data_pagamento, nome_cliente,
             valor_produto, valor_entrada, valor_saldo,
             tipo_pagamento, arquivo_comprovante, data_hora_registro)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        dados["numero_os"],
        dados.get("atendente", ""),
        dados.get("data_pagamento", ""),
        dados.get("nome_cliente", ""),
        dados.get("valor_produto", 0.0),
        dados.get("valor_entrada", 0.0),
        dados.get("valor_saldo", 0.0),
        dados.get("tipo_pagamento", ""),
        dados.get("arquivo_comprovante", ""),
        dados.get("data_hora_registro", datetime.now().strftime("%d/%m/%Y %H:%M:%S")),
    ))
    conn.commit()
    cur.close()
    conn.close()


def carregar_pagamentos() -> list[dict]:
    conn = get_conn()
    cur  = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM pagamentos ORDER BY id DESC")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


def contar_pagamentos() -> int:
    conn = get_conn()
    cur  = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM pagamentos")
    count = cur.fetchone()[0]
    cur.close()
    conn.close()
    return count


def atualizar_pagamento(id_: int, dados: dict):
    conn = get_conn()
    cur  = conn.cursor()
    cur.execute("""
        UPDATE pagamentos
        SET numero_os=%s, atendente=%s, data_pagamento=%s, nome_cliente=%s,
            valor_produto=%s, valor_entrada=%s, valor_saldo=%s, tipo_pagamento=%s
        WHERE id=%s
    """, (
        dados["numero_os"],
        dados.get("atendente", ""),
        dados.get("data_pagamento", ""),
        dados.get("nome_cliente", ""),
        dados.get("valor_produto", 0.0),
        dados.get("valor_entrada", 0.0),
        dados.get("valor_saldo", 0.0),
        dados.get("tipo_pagamento", ""),
        id_,
    ))
    conn.commit()
    cur.close()
    conn.close()


def excluir_pagamento(id_: int):
    conn = get_conn()
    cur  = conn.cursor()
    cur.execute("DELETE FROM pagamentos WHERE id=%s", (id_,))
    conn.commit()
    cur.close()
    conn.close()


# ═══════════════════════════════════════════════════════════════════════════════
# VENDEDORES
# ═══════════════════════════════════════════════════════════════════════════════

def listar_vendedores() -> list[dict]:
    conn = get_conn()
    cur  = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM vendedores ORDER BY nome")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


def cadastrar_vendedor(nome: str):
    conn = get_conn()
    cur  = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO vendedores (nome, criado_em)
            VALUES (%s, %s)
        """, (nome, datetime.now().strftime("%d/%m/%Y %H:%M:%S")))
        conn.commit()
    except IntegrityError:
        raise ValueError(f"Vendedor '{nome}' já cadastrado.")
    finally:
        cur.close()
        conn.close()


def excluir_vendedor(id_: int):
    conn = get_conn()
    cur  = conn.cursor()
    cur.execute("DELETE FROM vendedores WHERE id=%s", (id_,))
    conn.commit()
    cur.close()
    conn.close()