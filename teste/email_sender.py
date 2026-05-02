"""
╔══════════════════════════════════════════════════════════════════╗
║   MÓDULO DE ENVIO DE E-MAIL — Confirmação de Atendimento       ║
║   Envia e-mail automático ao cliente após cadastro              ║
╚══════════════════════════════════════════════════════════════════╝
"""

import smtplib
import os
import streamlit as st
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from notifications import registrar_notificacao

# ─────────────────────────────────────────────────────────────────
# CONFIGURAÇÃO SMTP (via st.secrets ou variáveis de ambiente)
# ─────────────────────────────────────────────────────────────────

def get_smtp_config():
    """Obtém configurações SMTP dos secrets ou variáveis de ambiente."""
    try:
        return {
            "host": st.secrets.get("SMTP_HOST", os.environ.get("SMTP_HOST", "smtp.gmail.com")),
            "port": int(st.secrets.get("SMTP_PORT", os.environ.get("SMTP_PORT", "587"))),
            "user": st.secrets.get("SMTP_USER", os.environ.get("SMTP_USER", "")),
            "password": st.secrets.get("SMTP_PASSWORD", os.environ.get("SMTP_PASSWORD", "")),
            "from_name": st.secrets.get("SMTP_FROM_NAME", os.environ.get("SMTP_FROM_NAME", "Samsung SMB")),
        }
    except Exception:
        return {
            "host": os.environ.get("SMTP_HOST", "smtp.gmail.com"),
            "port": int(os.environ.get("SMTP_PORT", "587")),
            "user": os.environ.get("SMTP_USER", ""),
            "password": os.environ.get("SMTP_PASSWORD", ""),
            "from_name": os.environ.get("SMTP_FROM_NAME", "Samsung SMB"),
        }

def email_configurado() -> bool:
    """Verifica se as configurações de e-mail estão definidas."""
    config = get_smtp_config()
    return bool(config["user"] and config["password"])

def enviar_confirmacao(email_destino: str, dados: dict) -> bool:
    """
    Envia e-mail de confirmação ao cliente após cadastro de atendimento.
    
    Parâmetros:
        email_destino (str): E-mail do cliente
        dados (dict): Dicionário com os dados do atendimento cadastrado
    
    Retorna:
        bool: True se enviado com sucesso, False caso contrário
    """
    config = get_smtp_config()
    
    if not config["user"] or not config["password"]:
        return False
    
    if not email_destino or "@" not in email_destino:
        return False
    
    try:
        # Monta a mensagem
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"✅ Confirmação de Atendimento — Pedido {dados['numero_pedido']}"
        msg["From"] = f"{config['from_name']} <{config['user']}>"
        msg["To"] = email_destino
        
        # Corpo do e-mail em HTML
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #034EA2 0%, #002E6E 100%); 
                           color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .header h1 {{ margin: 0; font-size: 24px; }}
                .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
                .field {{ margin: 15px 0; padding: 12px; background: white; border-left: 4px solid #034EA2; 
                          border-radius: 5px; }}
                .field-label {{ font-weight: bold; color: #034EA2; font-size: 12px; text-transform: uppercase; }}
                .field-value {{ font-size: 16px; margin-top: 4px; }}
                .footer {{ text-align: center; margin-top: 30px; font-size: 12px; color: #888; }}
                .highlight {{ color: #034EA2; font-weight: bold; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📱 Samsung — SMB</h1>
                    <p>Confirmação de Atendimento</p>
                </div>
                <div class="content">
                    <p>Olá, <strong>{dados['nome_cliente']}</strong>!</p>
                    <p>Seu atendimento foi <span class="highlight">cadastrado com sucesso</span> em nosso sistema.
                       Abaixo estão os detalhes do seu pedido:</p>
                    
                    <div class="field">
                        <div class="field-label">Número do Pedido</div>
                        <div class="field-value">{dados['numero_pedido']}</div>
                    </div>
                    
                    <div class="field">
                        <div class="field-label">Data do Atendimento</div>
                        <div class="field-value">{dados['data_atendimento']}</div>
                    </div>
                    
                    <div class="field">
                        <div class="field-label">Atendente Responsável</div>
                        <div class="field-value">{dados['atendente']}</div>
                    </div>
                    
                    <div class="field">
                        <div class="field-label">Valor do Pedido</div>
                        <div class="field-value">R$ {dados['valor_pedido']:,.2f}</div>
                    </div>
                    
                    <p style="margin-top: 25px; font-size: 14px; color: #666;">
                        Caso tenha alguma dúvida, entre em contato com nossa equipe.<br>
                        Agradecemos pela preferência!
                    </p>
                </div>
                <div class="footer">
                    <p>© Samsung SMB — Sistema de Cadastro de Atendimentos<br>
                    Este é um e-mail automático, por favor não responda.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(html_body, "html", "utf-8"))
        
        # Conecta ao servidor SMTP e envia
        with smtplib.SMTP(config["host"], config["port"], timeout=10) as server:
            server.starttls()
            server.login(config["user"], config["password"])
            server.send_message(msg)
        
        # Registra a notificação no banco de dados
        registrar_notificacao(
            tipo="email",
            destinatario=email_destino,
            assunto=f"✅ Confirmação de Atendimento — Pedido {dados['numero_pedido']}",
            mensagem=f"Confirmação de atendimento enviada para {dados['nome_cliente']}",
            status="enviada",
            referencia_tipo="atendimento",
        )
        
        return True
        
    except smtplib.SMTPAuthenticationError:
        raise RuntimeError("Falha na autenticação do e-mail. Verifique usuário e senha.")
    except smtplib.SMTPException as e:
        raise RuntimeError(f"Erro SMTP: {e}")
    except Exception as e:
        raise RuntimeError(f"Erro ao enviar e-mail: {e}")