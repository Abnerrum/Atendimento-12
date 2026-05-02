"""
╔══════════════════════════════════════════════════════════════════════════════╗
║   SISTEMA DE ATENDIMENTOS — Samsung SMB                                     ║
║   Interface Profissional | SQLite | Dashboard                               ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import streamlit as st
import pandas as pd
import io
import os
from datetime import datetime, date

# Garante que a pasta de comprovantes existe
os.makedirs("comprovantes", exist_ok=True)

from database import (
    salvar_atendimento,
    carregar_atendimentos,
    contar_atendimentos,
    obter_valor_total,
    estatisticas_por_atendente,
    estatisticas_por_periodo,
    evolucao_por_vendedor,
    limpar_todos_dados,
    atualizar_atendimento,
    listar_vendedores,
    cadastrar_vendedor,
    excluir_vendedor,
    salvar_pagamento,
    carregar_pagamentos,
    contar_pagamentos,
    excluir_pagamento,
    atualizar_pagamento,
)


# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURAÇÃO
# ═══════════════════════════════════════════════════════════════════════════════

def get_secret(key, default=None):
    try:
        val = st.secrets.get(key)
        if val is not None:
            return val
    except Exception:
        pass
    return os.environ.get(key, default)

st.set_page_config(
    page_title="Sistema de Atendimentos — Samsung SMB",
    page_icon="📱",
    layout="wide",
)

SENHA_ADMIN = get_secret("ADMIN_PASSWORD", "admin123")

# ═══════════════════════════════════════════════════════════════════════════════
# CSS
# ═══════════════════════════════════════════════════════════════════════════════

st.markdown("""
<style>
    .header-banner {
        background: linear-gradient(135deg, #034EA2 0%, #002E6E 100%);
        color: white;
        padding: 32px 40px;
        border-radius: 16px;
        text-align: center;
        margin-bottom: 28px;
    }
    .header-banner h1 { margin: 0; font-size: 2rem; }
    .header-banner p  { margin: 8px 0 0; opacity: 0.85; font-size: 1rem; }

    .metric-card {
        background: white;
        border: 1px solid #e5e9f0;
        border-radius: 12px;
        padding: 16px 12px;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,.06);
        min-height: 90px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
    }
    .metric-card .value {
        font-size: 1.45rem;
        font-weight: 700;
        color: #034EA2;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        max-width: 100%;
    }
    .metric-card .label {
        font-size: 0.78rem;
        color: #6b7280;
        margin-top: 4px;
        line-height: 1.3;
    }

    .calc-box {
        background: #f0f9ff;
        border: 1.5px solid #0ea5e9;
        border-radius: 12px;
        padding: 18px 24px;
        margin: 12px 0;
    }
    .calc-box .linha {
        display: flex; justify-content: space-between;
        font-size: 1rem; padding: 4px 0;
    }
    .calc-box .total {
        display: flex; justify-content: space-between;
        font-size: 1.15rem; font-weight: 700;
        border-top: 2px solid #0ea5e9; margin-top: 8px; padding-top: 8px;
    }
    .saldo-verde    { color: #059669; }
    .saldo-vermelho { color: #dc2626; }

    .success-box {
        background: #ecfdf5;
        border-left: 4px solid #10b981;
        padding: 16px 20px;
        border-radius: 8px;
        color: #065f46;
    }
    .section-title {
        font-size: 1.05rem;
        font-weight: 700;
        color: #034EA2;
        border-bottom: 2px solid #e5e9f0;
        padding-bottom: 6px;
        margin: 20px 0 14px;
    }
    .edit-box {
        background: #fffbeb;
        border: 1.5px solid #f59e0b;
        border-radius: 12px;
        padding: 20px 24px;
        margin: 16px 0;
    }
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# CABEÇALHO
# ═══════════════════════════════════════════════════════════════════════════════

st.markdown("""
<div class="header-banner">
    <h1>📱 REGISTRO DE ATENDIMENTO</h1>
    <p>Preencha os dados abaixo para registrar um novo atendimento Samsung</p>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# ABAS PRINCIPAIS
# ═══════════════════════════════════════════════════════════════════════════════

tab1, tab2, tab3 = st.tabs([
    "📝 PEDIDO SMB",
    "💳  PEDIDO CONTIGO",
    "🔐 Administração",
])

# ──────────────────────────────────────────────────────────────────────────────
# ABA 1 — VENDA SMB
# ──────────────────────────────────────────────────────────────────────────────

with tab1:
    st.subheader("Formulário de Cadastro")

    vendedores = listar_vendedores()
    nomes_vendedores = [v["nome"] for v in vendedores]

    if not nomes_vendedores:
        st.warning("⚠️ Nenhum vendedor cadastrado. Peça ao administrador para cadastrar os vendedores primeiro.")
    else:
        with st.form("form_atendimento", clear_on_submit=True):

            st.markdown("### 👤 Identificação do Atendente")
            col1, col2 = st.columns(2)
            with col1:
                atendente = st.selectbox("Atendente *", options=nomes_vendedores)
            with col2:
                data_atendimento = st.date_input("Data do Atendimento *", value=date.today())

            st.divider()
            st.markdown("### 🔢 Detalhes do Pedido")
            col3, col4 = st.columns(2)
            with col3:
                numero_pedido = st.text_input("Número do Pedido *", placeholder="Ex: PED-2024-001")
            with col4:
                valor_pedido = st.number_input("Valor do Pedido (R$) *", min_value=0.0, step=0.01, format="%.2f")

            st.divider()
            st.markdown("### 👥 Informações do Cliente")
            nome_cliente = st.text_input("Nome Completo do Cliente *", placeholder="Ex: João Silva")

            st.divider()
            st.markdown("### 📎 Comprovação")
            arquivo = st.file_uploader(
                "Anexar comprovante *",
                type=["pdf", "png", "jpg", "webp"],
                help="Formatos aceitos: PDF, PNG, JPG, WEBP",
            )
            st.caption("• Todos os campos marcados com * são obrigatórios")
            submetido = st.form_submit_button("✅ Cadastrar Atendimento", use_container_width=True)

        if submetido:
            erros = []
            if not numero_pedido.strip():    erros.append("Número do Pedido")
            if not nome_cliente.strip():     erros.append("Nome Completo do Cliente")
            if valor_pedido <= 0:            erros.append("Valor do Pedido (deve ser > 0)")
            if arquivo is None:              erros.append("Comprovante (obrigatório)")

            if erros:
                st.error(f"⚠️ Preencha os campos obrigatórios: {', '.join(erros)}.")
            else:
                # Salvar arquivo fisicamente
                nome_arquivo = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{arquivo.name}"
                caminho_salvar = os.path.join("comprovantes", nome_arquivo)
                with open(caminho_salvar, "wb") as f:
                    f.write(arquivo.getbuffer())

                dados = {
                    "atendente": atendente,
                    "data_atendimento": data_atendimento.strftime("%d/%m/%Y"),
                    "numero_pedido": numero_pedido.strip(),
                    "nome_cliente": nome_cliente.strip(),
                    "valor_pedido": float(valor_pedido),
                    "arquivo_comprovante": nome_arquivo,
                    "data_hora_registro": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                }
                try:
                    salvar_atendimento(dados)
                    
                    # Notificações Visuais Melhoradas
                    st.balloons()
                    st.toast(f"✅ Atendimento {numero_pedido} cadastrado com sucesso!", icon="🎉")
                    
                    # Mensagem de sucesso estilizada
                    st.markdown(f"""
                    <div style="background-color: #d4edda; color: #155724; padding: 20px; border-radius: 10px; border: 1px solid #c3e6cb; margin-bottom: 20px;">
                        <h4 style="margin-top: 0;">🎉 Cadastro Realizado com Sucesso!</h4>
                        <p>O atendimento para o cliente <b>{nome_cliente}</b> (Pedido: <b>{numero_pedido}</b>) foi registrado corretamente no sistema.</p>
                        <hr style="border-top: 1px solid #c3e6cb;">
                        <p style="font-size: 0.85rem; margin-bottom: 0;">Data/Hora do Registro: {dados['data_hora_registro']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Registrar notificação no sistema
                    from notifications import registrar_notificacao
                    registrar_notificacao(
                        tipo="sistema",
                        destinatario=atendente,
                        assunto="Novo Atendimento Cadastrado",
                        mensagem=f"Atendimento {numero_pedido} para {nome_cliente} cadastrado com sucesso.",
                        status="enviada",
                        referencia_tipo="atendimento"
                    )
                    
                    # Aguarda um pouco para o usuário ver a mensagem antes de recarregar
                    import time
                    time.sleep(2)
                    st.rerun()
                except ValueError as ve:
                    st.error(f"⚠️ {ve}")
                except Exception as ex:
                    st.error(f"❌ Erro ao salvar: {ex}")


# ──────────────────────────────────────────────────────────────────────────────
# ABA 2 — ATENDIMENTO CONTIGO
# ──────────────────────────────────────────────────────────────────────────────

with tab2:

    st.markdown("""
    <div style="background:linear-gradient(135deg,#034EA2,#0369a1);
                color:white;padding:20px 28px;border-radius:12px;margin-bottom:20px;">
        <h3 style="margin:0">💳 ATENDIMENTO CONTIGO</h3>
        <p style="margin:6px 0 0;opacity:.85;font-size:.9rem">
            Preencha todos os detalhes do pedido, informações do cliente,
            forma de pagamento e comprovante.
        </p>
    </div>
    """, unsafe_allow_html=True)

    with st.form("form_pagamento", clear_on_submit=True):

        st.markdown('<div class="section-title">🧾 1 · Detalhes do Pedido</div>', unsafe_allow_html=True)
        col_os1, col_os2, col_os3 = st.columns([2, 2, 2])
        with col_os1:
            numero_os = st.text_input("Número da OS *", placeholder="Ex: OS-2024-0042")
        with col_os2:
            atendente_pag = st.text_input("Nome do Atendente *", placeholder="Ex: João Silva")
        with col_os3:
            data_pag = st.date_input("Data *", value=date.today())

        st.markdown('<div class="section-title">👤 2 · Informações do Cliente</div>', unsafe_allow_html=True)
        col_c1, col_c2, col_c3 = st.columns(3)
        with col_c1:
            nome_cli = st.text_input("Nome do Cliente *", placeholder="Ex: Maria Oliveira")
        with col_c2:
            valor_produto = st.number_input("Valor do Produto (R$) *", min_value=0.0, step=0.01, format="%.2f")
        with col_c3:
            valor_entrada = st.number_input("Valor de Entrada (R$)", min_value=0.0, step=0.01, format="%.2f")

        valor_saldo = max(valor_produto - valor_entrada, 0.0)
        cor_saldo   = "saldo-verde" if valor_saldo == 0 else "saldo-vermelho"
        st.markdown(f"""
        <div class="calc-box">
            <div class="linha"><span>💰 Valor do Produto</span><span><strong>R$ {valor_produto:,.2f}</strong></span></div>
            <div class="linha"><span>✅ Entrada recebida</span><span><strong>R$ {valor_entrada:,.2f}</strong></span></div>
            <div class="total"><span>📌 Saldo Restante</span><span class="{cor_saldo}">R$ {valor_saldo:,.2f}</span></div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="section-title">💳 3 · Tipo de Pagamento</div>', unsafe_allow_html=True)
        tipo_pagamento = st.radio(
            "Forma de pagamento *",
            options=["💵 Espécie", "📲 PIX ou Transf.", "💳 Débito", "💳 Crédito"],
            horizontal=True,
            label_visibility="collapsed",
        )

        st.markdown('<div class="section-title">📎 4 · Comprovante de Pagamento</div>', unsafe_allow_html=True)
        comprovante = st.file_uploader(
            "Anexar comprovante de pagamento *",
            type=["pdf", "png", "jpg", "jpeg", "webp"],
            help="📌 Campo obrigatório",
            key="comp_pagamento",
        )
        if comprovante is not None:
            st.success(f"✅ Arquivo: **{comprovante.name}** ({comprovante.size / 1024:.1f} KB)")
        else:
            st.warning("⚠️ Comprovante é obrigatório.")

        st.caption("• Campos * obrigatórios  •  Data/hora registrada automaticamente")
        btn_pagar = st.form_submit_button("💾 Registrar Pagamento", use_container_width=True, type="primary")

    if btn_pagar:
        erros_pag = []
        if not numero_os.strip():      erros_pag.append("Número da OS")
        if not atendente_pag.strip():  erros_pag.append("Nome do Atendente")
        if not nome_cli.strip():       erros_pag.append("Nome do Cliente")
        if valor_produto <= 0:         erros_pag.append("Valor do Produto (deve ser > 0)")
        if comprovante is None:        erros_pag.append("Comprovante (obrigatório)")
        if valor_entrada > valor_produto:
            erros_pag.append("Entrada não pode ser maior que o Valor do Produto")

        if erros_pag:
            st.error(f"⚠️ Corrija: {', '.join(erros_pag)}.")
        else:
            # Salvar arquivo fisicamente
            nome_arquivo_pag = f"PAG_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{comprovante.name}"
            caminho_salvar_pag = os.path.join("comprovantes", nome_arquivo_pag)
            with open(caminho_salvar_pag, "wb") as f:
                f.write(comprovante.getbuffer())

            dados_pag = {
                "numero_os": numero_os.strip(),
                "atendente": atendente_pag.strip(),
                "data_pagamento": data_pag.strftime("%d/%m/%Y"),
                "nome_cliente": nome_cli.strip(),
                "valor_produto": float(valor_produto),
                "valor_entrada": float(valor_entrada),
                "valor_saldo": float(valor_saldo),
                "tipo_pagamento": tipo_pagamento,
                "arquivo_comprovante": nome_arquivo_pag,
                "data_hora_registro": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            }
            try:
                salvar_pagamento(dados_pag)
                
                # Notificações Visuais Melhoradas
                st.balloons()
                st.toast(f"✅ OS {numero_os.strip()} registrada com sucesso!", icon="💳")
                
                # Mensagem de sucesso estilizada
                st.markdown(f"""
                <div style="background-color: #d1ecf1; color: #0c5460; padding: 20px; border-radius: 10px; border: 1px solid #bee5eb; margin-bottom: 20px;">
                    <h4 style="margin-top: 0;">💳 Pagamento Registrado!</h4>
                    <p>A OS <b>{numero_os.strip()}</b> para o cliente <b>{nome_cli}</b> foi registrada com sucesso.</p>
                    <hr style="border-top: 1px solid #bee5eb;">
                    <p style="font-size: 0.85rem; margin-bottom: 0;">Data/Hora do Registro: {dados_pag['data_hora_registro']}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Registrar notificação no sistema
                from notifications import registrar_notificacao
                registrar_notificacao(
                    tipo="sistema",
                    destinatario=atendente_pag,
                    assunto="Novo Pagamento Registrado",
                    mensagem=f"Pagamento da OS {numero_os.strip()} para {nome_cli} registrado com sucesso.",
                    status="enviada",
                    referencia_tipo="pagamento"
                )
                
                st.markdown("---")
                st.markdown("#### 📋 Resumo")
                c1, c2, c3 = st.columns(3)
                c1.metric("OS", dados_pag["numero_os"])
                c2.metric("Atendente", dados_pag["atendente"])
                c3.metric("Data", dados_pag["data_pagamento"])
                cc1, cc2, cc3 = st.columns(3)
                cc1.metric("Cliente", dados_pag["nome_cliente"])
                cc2.metric("Pagamento", dados_pag["tipo_pagamento"])
                cc3.metric("Valor Produto", f"R$ {dados_pag['valor_produto']:,.2f}")
                ccc1, ccc2, ccc3 = st.columns(3)
                ccc1.metric("Entrada", f"R$ {dados_pag['valor_entrada']:,.2f}")
                ccc2.metric(
                    "Saldo Restante", f"R$ {dados_pag['valor_saldo']:,.2f}",
                    delta="Quitado ✅" if dados_pag["valor_saldo"] == 0 else f"- R$ {dados_pag['valor_saldo']:,.2f}",
                    delta_color="normal" if dados_pag["valor_saldo"] == 0 else "inverse",
                )
            except Exception as ex:
                st.error(f"❌ Erro ao registrar: {ex}")


# ──────────────────────────────────────────────────────────────────────────────
# ABA 3 — ADMINISTRAÇÃO
# ──────────────────────────────────────────────────────────────────────────────

with tab3:
    st.subheader("🔐 Painel de Controle")
    senha_input = st.text_input("Senha de Administrador", type="password")

    if senha_input == SENHA_ADMIN:

        total_atend  = contar_atendimentos()
        valor_total  = obter_valor_total()
        ticket_medio = (valor_total / total_atend) if total_atend > 0 else 0.0
        total_pag    = contar_pagamentos()

        def fmt_val(v):
            if v >= 1_000_000: return f"R$ {v/1_000_000:.1f}M"
            if v >= 10_000:    return f"R$ {v:,.0f}"
            return f"R$ {v:,.2f}"

        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        for col, val, lbl in [
            (col_m1, total_atend,           "Atendimentos Cadastrados"),
            (col_m2, fmt_val(valor_total),  "Valor Total Acumulado"),
            (col_m3, fmt_val(ticket_medio), "Ticket Médio"),
            (col_m4, total_pag,             "Pagamentos Registrados"),
        ]:
            col.markdown(f"""
            <div class="metric-card">
                <div class="value">{val}</div>
                <div class="label">{lbl}</div>
            </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        subtab1, subtab2, subtab3, subtab4, subtab5 = st.tabs([
            "📋 Histórico Atendimentos",
            "💳 Histórico Pagamentos",
            "📊 Dashboard de Análise",
            "👥 Gestão de Vendedores",
            "🔔 Notificações",
        ])

        # ════════════════════════════════════════
        # HISTÓRICO ATENDIMENTOS
        # ════════════════════════════════════════
        with subtab1:
            atendimentos = carregar_atendimentos()
            if atendimentos:
                df = pd.DataFrame(atendimentos)
                df_display = df[[
                    "id","atendente","data_atendimento","numero_pedido",
                    "nome_cliente","valor_pedido",
                    "arquivo_comprovante","data_hora_registro",
                ]].rename(columns={
                    "id":"ID","atendente":"Atendente","data_atendimento":"Data",
                    "numero_pedido":"Nº Pedido","nome_cliente":"Cliente",
                    "valor_pedido":"Valor (R$)",
                    "arquivo_comprovante":"Comprovante","data_hora_registro":"Registrado em",
                })
                st.metric("Total de Registros", len(df_display))
                st.dataframe(df_display, use_container_width=True)

                buffer = io.BytesIO()
                df_display.to_excel(buffer, index=False, engine="openpyxl")
                buffer.seek(0)
                st.download_button(
                    "📥 Baixar Excel", data=buffer,
                    file_name=f"atendimentos_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )

                st.markdown("---")
                st.markdown("### ✏️ Editar Atendimento")
                ids_disp = [r["id"] for r in atendimentos]
                id_editar = st.selectbox(
                    "Selecione o ID:",
                    ids_disp,
                    format_func=lambda x: f"ID {x} — " + next(
                        (f"{r['numero_pedido']} | {r['nome_cliente']}" for r in atendimentos if r["id"] == x), ""
                    ),
                )
                registro = next((r for r in atendimentos if r["id"] == id_editar), None)
                if registro:
                    vendedores_admin = listar_vendedores()
                    nomes_admin = [v["nome"] for v in vendedores_admin]
                    if registro["atendente"] not in nomes_admin:
                        nomes_admin.insert(0, registro["atendente"])
                    with st.form(f"form_editar_{id_editar}"):
                        ce1, ce2 = st.columns(2)
                        with ce1:
                            idx = nomes_admin.index(registro["atendente"]) if registro["atendente"] in nomes_admin else 0
                            ed_at  = st.selectbox("Atendente", nomes_admin, index=idx)
                            ed_ped = st.text_input("Nº Pedido", value=registro["numero_pedido"])
                            ed_cli = st.text_input("Cliente", value=registro["nome_cliente"])
                        with ce2:
                            try:
                                dt_p = datetime.strptime(registro["data_atendimento"], "%d/%m/%Y").date()
                            except Exception:
                                dt_p = date.today()
                            ed_dt  = st.date_input("Data", value=dt_p)
                            ed_val = st.number_input("Valor (R$)", value=float(registro["valor_pedido"]), min_value=0.0, step=0.01, format="%.2f")
                        salvar_ed = st.form_submit_button("💾 Salvar Alterações", use_container_width=True)
                    if salvar_ed:
                        try:
                            atualizar_atendimento(id_editar, {
                                "atendente": ed_at,
                                "data_atendimento": ed_dt.strftime("%d/%m/%Y"),
                                "numero_pedido": ed_ped.strip(),
                                "nome_cliente": ed_cli.strip(),
                                "valor_pedido": float(ed_val),
                            })
                            st.toast(f"✏️ Atendimento ID {id_editar} atualizado!", icon="✅")
                            st.success(f"✅ Atendimento ID {id_editar} atualizado com sucesso!")
                            st.rerun()
                        except Exception as ex:
                            st.error(f"❌ {ex}")

                st.markdown("---")
                st.markdown("### 🗑️ Zona de Perigo")
                # ── Mostrar comprovantes anexados ──────────────────────
                st.markdown("---")
                st.markdown("### 📎 Comprovantes Anexados")
                comprovantes_atend = [r for r in atendimentos if r.get("arquivo_comprovante")]
                if comprovantes_atend:
                    for r in comprovantes_atend:
                        nome_arq = r['arquivo_comprovante']
                        caminho_arq = os.path.join("comprovantes", nome_arq)
                        
                        with st.expander(f"📄 ID {r['id']} — {r['nome_cliente']} | {r['numero_pedido']}"):
                            st.markdown(f"**Arquivo:** `{nome_arq}`")
                            st.caption(f"Atendente: {r['atendente']} | Valor: R$ {float(r['valor_pedido']):,.2f}")
                            
                            if os.path.exists(caminho_arq):
                                with open(caminho_arq, "rb") as f:
                                    btn_data = f.read()
                                
                                col_v1, col_v2 = st.columns(2)
                                with col_v1:
                                    st.download_button(
                                        label="📥 Baixar Comprovante",
                                        data=btn_data,
                                        file_name=nome_arq,
                                        mime="application/octet-stream",
                                        key=f"btn_dl_{r['id']}"
                                    )
                                with col_v2:
                                    ext = nome_arq.split('.')[-1].lower()
                                    if ext in ['png', 'jpg', 'jpeg', 'webp']:
                                        st.image(caminho_arq, caption="Visualização do Comprovante", use_container_width=True)
                                    elif ext == 'pdf':
                                        st.info("Arquivo PDF - Use o botão de baixar para visualizar.")
                            else:
                                st.error("⚠️ Arquivo não encontrado no servidor.")
                else:
                    st.info("Nenhum comprovante registrado.")

                st.markdown("---")
                st.markdown("### 🗑️ Zona de Perigo")
                if st.button("🗑️ Limpar Todos os Atendimentos", type="secondary"):
                    if st.session_state.get("confirmar_limpeza"):
                        try:
                            limpar_todos_dados()
                            st.toast("🗑️ Todos os atendimentos foram removidos!", icon="⚠️")
                            st.success("✅ Todos os atendimentos foram removidos.")
                            st.session_state["confirmar_limpeza"] = False
                            st.rerun()
                        except Exception as ex:
                            st.error(f"❌ {ex}")
                    else:
                        st.session_state["confirmar_limpeza"] = True
                        st.warning("⚠️ Clique novamente para confirmar.")
            else:
                st.info("Nenhum atendimento cadastrado ainda.")

        # ════════════════════════════════════════
        # HISTÓRICO PAGAMENTOS
        # ════════════════════════════════════════
        with subtab2:
            pagamentos = carregar_pagamentos()
            if pagamentos:
                df_pag = pd.DataFrame(pagamentos)
                df_pag_display = df_pag[[
                    "id","numero_os","atendente","data_pagamento","nome_cliente","valor_produto",
                    "valor_entrada","valor_saldo","tipo_pagamento",
                    "arquivo_comprovante","data_hora_registro",
                ]].rename(columns={
                    "id":"ID","numero_os":"Nº OS","atendente":"Atendente","data_pagamento":"Data",
                    "nome_cliente":"Cliente","valor_produto":"Valor Produto (R$)","valor_entrada":"Entrada (R$)",
                    "valor_saldo":"Saldo (R$)","tipo_pagamento":"Pagamento",
                    "arquivo_comprovante":"Comprovante","data_hora_registro":"Registrado em",
                })

                total_pag_val  = df_pag["valor_produto"].sum()
                total_entradas = df_pag["valor_entrada"].sum()
                total_saldo    = df_pag["valor_saldo"].sum()

                cp1, cp2, cp3 = st.columns(3)
                cp1.metric("💰 Total Vendido",   f"R$ {total_pag_val:,.2f}")
                cp2.metric("✅ Total Recebido",  f"R$ {total_entradas:,.2f}")
                cp3.metric("📌 Total a Receber", f"R$ {total_saldo:,.2f}")

                st.markdown("### 📎 Comprovantes de Pagamento")
                comprovantes_pag = [r for r in pagamentos if r.get("arquivo_comprovante")]
                if comprovantes_pag:
                    # Criar uma lista de seleção para visualizar comprovantes específicos
                    opcoes_comp = [f"OS {r['numero_os']} — {r['nome_cliente']}" for r in comprovantes_pag]
                    selecionado = st.selectbox("Selecione um comprovante para visualizar:", ["Selecione..."] + opcoes_comp, key="sel_comp_pag_view")
                    
                    if selecionado != "Selecione...":
                        idx_sel = opcoes_comp.index(selecionado)
                        r = comprovantes_pag[idx_sel]
                        nome_arq = r['arquivo_comprovante']
                        caminho_arq = os.path.join("comprovantes", nome_arq)
                        
                        st.info(f"Visualizando: **{nome_arq}**")
                        if os.path.exists(caminho_arq):
                            with open(caminho_arq, "rb") as f:
                                btn_data = f.read()
                            
                            col_p1, col_p2 = st.columns([1, 2])
                            with col_p1:
                                st.download_button(
                                    label="📥 Baixar Comprovante",
                                    data=btn_data,
                                    file_name=nome_arq,
                                    mime="application/octet-stream",
                                    key=f"btn_dl_pag_sel_{r['id']}"
                                )
                                st.markdown(f"**OS:** {r['numero_os']}")
                                st.markdown(f"**Cliente:** {r['nome_cliente']}")
                                st.markdown(f"**Valor:** R$ {float(r['valor_produto']):,.2f}")
                            with col_p2:
                                ext = nome_arq.split('.')[-1].lower()
                                if ext in ['png', 'jpg', 'jpeg', 'webp']:
                                    st.image(caminho_arq, use_container_width=True)
                                elif ext == 'pdf':
                                    st.warning("Arquivo PDF - Use o botão de baixar para visualizar.")
                        else:
                            st.error("⚠️ Arquivo não encontrado no servidor.")
                else:
                    st.info("Nenhum comprovante de pagamento registrado.")

                st.markdown("---")
                st.markdown("### 📊 Tabela de Registros")
                st.dataframe(df_pag_display, use_container_width=True)

                buf2 = io.BytesIO()
                df_pag_display.to_excel(buf2, index=False, engine="openpyxl")
                buf2.seek(0)
                st.download_button(
                    "📥 Baixar Pagamentos em Excel", data=buf2,
                    file_name=f"pagamentos_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )

                st.markdown("---")
                st.markdown("### ✏️ Editar Registro de Pagamento")
                ids_pag = [r["id"] for r in pagamentos]
                id_edit_pag = st.selectbox(
                    "Selecione o registro para editar:",
                    ids_pag,
                    format_func=lambda x: f"ID {x} — " + next(
                        (f"{r['numero_os']} | {r['nome_cliente']}" for r in pagamentos if r["id"] == x), ""
                    ),
                    key="sel_edit_pag",
                )

                reg_pag = next((r for r in pagamentos if r["id"] == id_edit_pag), None)
                if reg_pag:
                    with st.form(f"form_edit_pag_{id_edit_pag}"):

                        st.markdown("##### 🧾 Detalhes do Pedido")
                        ep1, ep2, ep3 = st.columns(3)
                        with ep1:
                            ep_os    = st.text_input("Nº OS", value=reg_pag["numero_os"])
                        with ep2:
                            ep_atend = st.text_input("Atendente", value=reg_pag.get("atendente", ""))
                        with ep3:
                            try:
                                dt_pag_edit = datetime.strptime(reg_pag.get("data_pagamento", datetime.now().strftime("%d/%m/%Y")), "%d/%m/%Y").date()
                            except Exception:
                                dt_pag_edit = date.today()
                            ep_dt = st.date_input("Data", value=dt_pag_edit)

                        st.markdown("##### 👤 Informações do Cliente")
                        ec1, ec2, ec3 = st.columns(3)
                        with ec1:
                            ep_cli   = st.text_input("Nome do Cliente", value=reg_pag["nome_cliente"])
                        with ec2:
                            ep_vprod = st.number_input("Valor do Produto (R$)", value=float(reg_pag["valor_produto"]), min_value=0.0, step=0.01, format="%.2f")
                        with ec3:
                            ep_vent  = st.number_input("Valor de Entrada (R$)", value=float(reg_pag["valor_entrada"]), min_value=0.0, step=0.01, format="%.2f")

                        ep_saldo = max(ep_vprod - ep_vent, 0.0)
                        cor = "saldo-verde" if ep_saldo == 0 else "saldo-vermelho"
                        st.markdown(f"""
                        <div class="calc-box">
                            <div class="linha"><span>💰 Valor Produto</span><span><b>R$ {ep_vprod:,.2f}</b></span></div>
                            <div class="linha"><span>✅ Entrada</span><span><b>R$ {ep_vent:,.2f}</b></span></div>
                            <div class="total"><span>📌 Saldo Restante</span><span class="{cor}">R$ {ep_saldo:,.2f}</span></div>
                        </div>
                        """, unsafe_allow_html=True)

                        st.markdown("##### 💳 Tipo de Pagamento")
                        opcoes_pag = ["💵 Espécie", "📲 PIX ou Transf.", "💳 Débito", "💳 Crédito"]
                        idx_pag    = opcoes_pag.index(reg_pag["tipo_pagamento"]) if reg_pag["tipo_pagamento"] in opcoes_pag else 0
                        ep_tipo = st.radio(
                            "Forma de pagamento", options=opcoes_pag,
                            index=idx_pag, horizontal=True,
                            label_visibility="collapsed",
                        )

                        col_save, col_del = st.columns([3, 1])
                        with col_save:
                            btn_salvar_pag  = st.form_submit_button("💾 Salvar Alterações", use_container_width=True, type="primary")
                        with col_del:
                            btn_excluir_pag = st.form_submit_button("🗑️ Excluir", use_container_width=True)

                    if btn_salvar_pag:
                        try:
                            atualizar_pagamento(id_edit_pag, {
                                "numero_os":      ep_os.strip(),
                                "atendente":      ep_atend.strip(),
                                "data_pagamento": ep_dt.strftime("%d/%m/%Y"),
                                "nome_cliente":   ep_cli.strip(),
                                "valor_produto":  float(ep_vprod),
                                "valor_entrada":  float(ep_vent),
                                "valor_saldo":    float(ep_saldo),
                                "tipo_pagamento": ep_tipo,
                            })
                            st.toast(f"✏️ Pagamento ID {id_edit_pag} atualizado!", icon="✅")
                            st.success(f"✅ Registro ID {id_edit_pag} atualizado com sucesso!")
                            st.rerun()
                        except Exception as ex:
                            st.error(f"❌ {ex}")

                    if btn_excluir_pag:
                        try:
                            excluir_pagamento(id_edit_pag)
                            st.toast(f"🗑️ Pagamento ID {id_edit_pag} excluído!", icon="⚠️")
                            st.success(f"✅ Registro ID {id_edit_pag} excluído com sucesso.")
                            st.rerun()
                        except Exception as ex:
                            st.error(f"❌ {ex}")

                # ── Mostrar comprovantes de pagamento ──────────────────────
                st.markdown("---")
                st.markdown("### 📎 Comprovantes de Pagamento")
                comprovantes_pag = [r for r in pagamentos if r.get("arquivo_comprovante")]
                if comprovantes_pag:
                    for r in comprovantes_pag:
                        nome_arq = r['arquivo_comprovante']
                        caminho_arq = os.path.join("comprovantes", nome_arq)
                        
                        with st.expander(f"📄 ID {r['id']} — {r['nome_cliente']} | OS: {r['numero_os']} | {r['data_pagamento']}"):
                            st.markdown(f"**Arquivo:** `{nome_arq}`")
                            st.caption(f"Atendente: {r['atendente']} | Valor: R$ {float(r['valor_produto']):,.2f} | Tipo: {r['tipo_pagamento']}")
                            
                            if os.path.exists(caminho_arq):
                                with open(caminho_arq, "rb") as f:
                                    btn_data = f.read()
                                
                                col_v1, col_v2 = st.columns([1, 2])
                                with col_v1:
                                    st.download_button(
                                        label="📥 Baixar Comprovante",
                                        data=btn_data,
                                        file_name=nome_arq,
                                        mime="application/octet-stream",
                                        key=f"btn_dl_pag_admin_{r['id']}"
                                    )
                                with col_v2:
                                    ext = nome_arq.split('.')[-1].lower()
                                    if ext in ['png', 'jpg', 'jpeg', 'webp']:
                                        st.image(caminho_arq, caption="Visualização do Pagamento", use_container_width=True)
                                    elif ext == 'pdf':
                                        st.info("📄 Arquivo PDF - Use o botão ao lado para baixar e visualizar.")
                                        # Opcional: Tentar exibir PDF se o navegador suportar (Streamlit não tem nativo simples sem base64)
                            else:
                                st.error("⚠️ Arquivo não encontrado no servidor.")
                else:
                    st.info("Nenhum comprovante registrado.")

            else:
                st.info("Nenhum pagamento registrado ainda.")

        # ════════════════════════════════════════
        # DASHBOARD
        # ════════════════════════════════════════
        with subtab3:
            st.markdown("### 📊 Análise de Atendimentos")
            stats_atendente = estatisticas_por_atendente()
            if not stats_atendente:
                st.info("Sem dados suficientes.")
            else:
                df_at = pd.DataFrame(stats_atendente)
                df_resumo = df_at.rename(columns={
                    "atendente":"Vendedor","total_atendimentos":"Total Vendas",
                    "valor_total":"Valor Total (R$)","valor_medio":"Ticket Médio (R$)",
                })
                df_resumo["Valor Total (R$)"]  = df_resumo["Valor Total (R$)"].map(lambda x: f"R$ {x:,.2f}")
                df_resumo["Ticket Médio (R$)"] = df_resumo["Ticket Médio (R$)"].map(lambda x: f"R$ {x:,.2f}")
                st.markdown("#### 🏆 Ranking de Vendedores")
                st.dataframe(df_resumo, use_container_width=True, hide_index=True)
                st.markdown("---")
                cg1, cg2 = st.columns(2)
                with cg1:
                    st.markdown("**Quantidade de Vendas**")
                    st.bar_chart(df_at.set_index("atendente")["total_atendimentos"], color="#034EA2")
                with cg2:
                    st.markdown("**Faturamento Total (R$)**")
                    st.bar_chart(df_at.set_index("atendente")["valor_total"], color="#10b981")

        # ════════════════════════════════════════
        # VENDEDORES
        # ════════════════════════════════════════
        with subtab4:
            st.markdown("### 👥 Cadastro de Vendedores")
            with st.form("form_novo_vendedor", clear_on_submit=True):
                cv1, cv2 = st.columns([3, 1])
                with cv1:
                    novo_vendedor = st.text_input("Nome do Vendedor", placeholder="Ex: Maria Santos")
                with cv2:
                    st.markdown("<br>", unsafe_allow_html=True)
                    btn_cad = st.form_submit_button("➕ Cadastrar", use_container_width=True)

            if btn_cad:
                if not novo_vendedor.strip():
                    st.error("⚠️ Informe o nome.")
                else:
                    try:
                        cadastrar_vendedor(novo_vendedor.strip())
                        st.toast(f"👤 Vendedor {novo_vendedor.strip()} cadastrado!", icon="✅")
                        st.success(f"✅ Vendedor **{novo_vendedor.strip()}** cadastrado!")
                        st.rerun()
                    except ValueError as ve:
                        st.error(f"⚠️ {ve}")
                    except Exception as ex:
                        st.error(f"❌ {ex}")

            st.markdown("---")
            st.markdown("### 📋 Vendedores Cadastrados")
            vendedores_lista = listar_vendedores()
            if not vendedores_lista:
                st.info("Nenhum vendedor cadastrado.")
            else:
                st.markdown(f"**Total: {len(vendedores_lista)} vendedor(es)**")
                for v in vendedores_lista:
                    cn, cd, cb = st.columns([3, 2, 1])
                    with cn: st.markdown(f"👤 **{v['nome']}**")
                    with cd: st.caption(f"Cadastrado em: {v['criado_em']}")
                    with cb:
                        if st.button("🗑️", key=f"del_{v['id']}", help=f"Excluir {v['nome']}"):
                            try:
                                excluir_vendedor(v["id"])
                                st.toast(f"🗑️ Vendedor {v['nome']} excluído!", icon="⚠️")
                                st.success(f"✅ **{v['nome']}** excluído.")
                                st.rerun()
                            except Exception as ex:
                                st.error(f"❌ {ex}")
                    st.divider()

        # ════════════════════════════════════════
        # NOTIFICAÇÕES
        # ════════════════════════════════════════
        with subtab5:
            from notifications import carregar_notificacoes, obter_estatisticas_notificacoes, marcar_todas_como_lidas
            
            st.markdown("### 🔔 Histórico de Notificações")
            
            stats = obter_estatisticas_notificacoes()
            sn1, sn2, sn3 = st.columns(3)
            sn1.metric("Total Enviadas", stats["total"])
            sn2.metric("Não Lidas", stats["nao_lidas"])
            
            if st.button("Marcar todas como lidas"):
                marcar_todas_como_lidas()
                st.rerun()
                
            notifs = carregar_notificacoes(limite=100)
            if notifs:
                df_notif = pd.DataFrame(notifs)
                # Formatação para exibição
                df_notif_display = df_notif[[
                    "id", "tipo", "destinatario", "assunto", "mensagem", "status", "data_hora_envio", "lido"
                ]].rename(columns={
                    "id": "ID", "tipo": "Tipo", "destinatario": "Destinatário", 
                    "assunto": "Assunto", "mensagem": "Mensagem", "status": "Status", 
                    "data_hora_envio": "Enviado em", "lido": "Lido"
                })
                
                # Estilização básica: ícones para tipos
                df_notif_display["Tipo"] = df_notif_display["Tipo"].apply(
                    lambda x: "📧 E-mail" if x == "email" else ("📱 Sistema" if x == "sistema" else x)
                )
                
                st.dataframe(df_notif_display, use_container_width=True)
            else:
                st.info("Nenhuma notificação registrada.")

    elif senha_input:
        st.error("❌ Senha incorreta.")

# ═══════════════════════════════════════════════════════════════════════════════
# RODAPÉ
# ═══════════════════════════════════════════════════════════════════════════════

st.markdown("---")
st.caption("📱 Sistema de Cadastro de Atendimentos — Samsung SMB | Versão 4.2")