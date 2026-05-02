"""
╔══════════════════════════════════════════════════════════════════════════════╗
║   MÓDULO DE NOTIFICAÇÕES — Sistema de Atendimentos Samsung SMB              ║
║   MySQL (Workbench) | Histórico de notificações e preferências              ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from datetime import datetime
from typing import Optional
from database import get_conn   # reutiliza o pool MySQL do database.py


# ─────────────────────────────────────────────────────────────────────────────
# INICIALIZAÇÃO DAS TABELAS
# ─────────────────────────────────────────────────────────────────────────────

def init_notifications_table():
    conn = get_conn()
    cur  = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS notificacoes (
            id               INT          AUTO_INCREMENT PRIMARY KEY,
            tipo             VARCHAR(30)  NOT NULL,
            destinatario     VARCHAR(200) NOT NULL,
            assunto          VARCHAR(300) DEFAULT '',
            mensagem         TEXT,
            status           VARCHAR(30)  DEFAULT 'enviada',
            data_hora_envio  VARCHAR(30)  DEFAULT '',
            referencia_id    INT          DEFAULT NULL,
            referencia_tipo  VARCHAR(50)  DEFAULT NULL,
            lido             TINYINT(1)   DEFAULT 0
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS preferencias_notificacao (
            id                INT          AUTO_INCREMENT PRIMARY KEY,
            usuario           VARCHAR(150) NOT NULL UNIQUE,
            email_atendimento TINYINT(1)   DEFAULT 1,
            email_pagamento   TINYINT(1)   DEFAULT 1,
            notif_sistema     TINYINT(1)   DEFAULT 1,
            criada_em         VARCHAR(30)  DEFAULT ''
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """)

    conn.commit()
    cur.close()
    conn.close()


# Inicializa ao importar
init_notifications_table()


# ═══════════════════════════════════════════════════════════════════════════════
# FUNÇÕES DE NOTIFICAÇÃO
# ═══════════════════════════════════════════════════════════════════════════════

def registrar_notificacao(
    tipo: str,
    destinatario: str,
    assunto: str,
    mensagem: str,
    status: str = "enviada",
    referencia_id: Optional[int] = None,
    referencia_tipo: Optional[str] = None,
) -> int:
    conn = get_conn()
    cur  = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO notificacoes
                (tipo, destinatario, assunto, mensagem, status,
                 data_hora_envio, referencia_id, referencia_tipo)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            tipo,
            destinatario,
            assunto,
            mensagem,
            status,
            datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            referencia_id,
            referencia_tipo,
        ))
        conn.commit()
        return cur.lastrowid
    finally:
        cur.close()
        conn.close()


def carregar_notificacoes(limite: int = 50) -> list[dict]:
    conn = get_conn()
    cur  = conn.cursor(dictionary=True)
    cur.execute(
        "SELECT * FROM notificacoes ORDER BY id DESC LIMIT %s",
        (limite,)
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


def carregar_notificacoes_por_tipo(tipo: str, limite: int = 50) -> list[dict]:
    conn = get_conn()
    cur  = conn.cursor(dictionary=True)
    cur.execute(
        "SELECT * FROM notificacoes WHERE tipo=%s ORDER BY id DESC LIMIT %s",
        (tipo, limite)
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


def contar_notificacoes_nao_lidas() -> int:
    conn = get_conn()
    cur  = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM notificacoes WHERE lido=0")
    count = cur.fetchone()[0]
    cur.close()
    conn.close()
    return count


def marcar_como_lida(notif_id: int):
    conn = get_conn()
    cur  = conn.cursor()
    cur.execute("UPDATE notificacoes SET lido=1 WHERE id=%s", (notif_id,))
    conn.commit()
    cur.close()
    conn.close()


def marcar_todas_como_lidas():
    conn = get_conn()
    cur  = conn.cursor()
    cur.execute("UPDATE notificacoes SET lido=1")
    conn.commit()
    cur.close()
    conn.close()


def obter_preferencias_notificacao(usuario: str) -> dict:
    conn = get_conn()
    cur  = conn.cursor(dictionary=True)
    cur.execute(
        "SELECT * FROM preferencias_notificacao WHERE usuario=%s",
        (usuario,)
    )
    row = cur.fetchone()
    cur.close()
    conn.close()

    if row:
        return row
    return {
        "usuario": usuario,
        "email_atendimento": True,
        "email_pagamento":   True,
        "notif_sistema":     True,
    }


def salvar_preferencias_notificacao(usuario: str, prefs: dict):
    conn = get_conn()
    cur  = conn.cursor()
    try:
        # INSERT … ON DUPLICATE KEY UPDATE — atômico no MySQL
        cur.execute("""
            INSERT INTO preferencias_notificacao
                (usuario, email_atendimento, email_pagamento, notif_sistema, criada_em)
            VALUES (%s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                email_atendimento = VALUES(email_atendimento),
                email_pagamento   = VALUES(email_pagamento),
                notif_sistema     = VALUES(notif_sistema)
        """, (
            usuario,
            prefs.get("email_atendimento", True),
            prefs.get("email_pagamento",   True),
            prefs.get("notif_sistema",     True),
            datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        ))
        conn.commit()
    finally:
        cur.close()
        conn.close()


def limpar_notificacoes_antigas(dias: int = 30):
    conn = get_conn()
    cur  = conn.cursor()
    cur.execute("""
        DELETE FROM notificacoes
        WHERE STR_TO_DATE(data_hora_envio, '%%d/%%m/%%Y %%H:%%i:%%s')
              < DATE_SUB(NOW(), INTERVAL %s DAY)
    """, (dias,))
    conn.commit()
    cur.close()
    conn.close()


def obter_estatisticas_notificacoes() -> dict:
    conn = get_conn()
    cur  = conn.cursor(dictionary=True)

    cur.execute("SELECT COUNT(*) AS total FROM notificacoes")
    total = cur.fetchone()["total"]

    cur.execute("SELECT COUNT(*) AS nao_lidas FROM notificacoes WHERE lido=0")
    nao_lidas = cur.fetchone()["nao_lidas"]

    cur.execute("""
        SELECT
            tipo,
            COUNT(*) AS total,
            SUM(status = 'enviada') AS enviadas,
            SUM(status = 'falha')   AS falhas
        FROM notificacoes
        GROUP BY tipo
    """)
    por_tipo = cur.fetchall()

    cur.close()
    conn.close()

    return {
        "total":     total,
        "nao_lidas": nao_lidas,
        "por_tipo":  por_tipo,
    }