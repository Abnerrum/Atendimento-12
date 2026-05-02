# 📱 Sistema de Cadastro de Atendimentos — Samsung SMB

Sistema web completo para cadastro e gerenciamento de atendimentos, construído com **Streamlit** e **SQLite**.

---

## ✨ Funcionalidades

| Funcionalidade | Descrição |
|---|---|
| 📝 **Cadastro de Atendimentos** | Formulário intuitivo com todos os campos necessários |
| 💾 **Banco de Dados SQLite** | Persistência local, sem dependência de serviços externos |
| 📊 **Dashboard com Gráficos** | Visualizações por atendente (barras) e por período (linhas) |
| 📧 **Envio Automático de E-mail** | Confirmação enviada ao cliente após cada cadastro |
| 🔐 **Área Administrativa** | Acesso protegido por senha para visualizar histórico e métricas |
| 📥 **Exportação Excel** | Download do histórico completo em formato .xlsx |
| 📱 **Design Responsivo** | Interface adaptada para desktop e mobile |

---

## 📁 Estrutura do Projeto

```
cadastro_atendimentos/
├── streamlit_app.py          ← Aplicação principal (Streamlit)
├── database.py               ← Módulo de banco de dados SQLite
├── email_sender.py           ← Módulo de envio de e-mail SMTP
├── requirements.txt          ← Dependências do projeto
├── .streamlit/
│   └── config.toml           ← Configurações do Streamlit
├── .env.example              ← Exemplo de variáveis de ambiente
├── atendimentos.db           ← Banco de dados (gerado automaticamente)
└── README.md                 ← Este arquivo
```

---

## 🚀 Instalação Local

### 1. Clone ou baixe o projeto

```bash
cd cadastro_atendimentos
```

### 2. Crie um ambiente virtual (recomendado)

```bash
python -m venv venv

# Windows:
venv\Scripts\activate

# Linux/macOS:
source venv/bin/activate
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. Configure as variáveis de ambiente (opcional)

```bash
# Copie o arquivo de exemplo:
cp .env.example .env

# Edite o arquivo .env com seus dados reais
```

Ou configure diretamente no terminal:

```bash
# Windows:
set ADMIN_PASSWORD=sua_senha_aqui
set SMTP_USER=seu-email@gmail.com
set SMTP_PASSWORD=sua-senha-de-app

# Linux/macOS:
export ADMIN_PASSWORD=sua_senha_aqui
export SMTP_USER=seu-email@gmail.com
export SMTP_PASSWORD=sua-senha-de-app
```

### 5. Execute a aplicação

```bash
streamlit run streamlit_app.py
```

Acesse no navegador: **http://localhost:8501**

---

## ☁️ Deploy Gratuito na Nuvem

### Opção 1: Streamlit Cloud (Recomendada — Grátis)

1. Crie uma conta em [streamlit.io/cloud](https://streamlit.io/cloud)
2. Conecte sua conta ao GitHub
3. Crie um novo repositório no GitHub e envie os arquivos:

```bash
# Inicialize o repositório
git init
git add .
git commit -m "Primeiro commit"

# Crie um repositório no GitHub e conecte:
git remote add origin https://github.com/SEU_USUARIO/NOME_DO_REPO.git
git branch -M main
git push -u origin main
```

4. No Streamlit Cloud, clique em **"New app"**
5. Selecione o repositório, branch `main` e arquivo `streamlit_app.py`
6. Configure os **Secrets** (Menu ⚙️ → Secrets):

```toml
ADMIN_PASSWORD = "sua_senha_segura_aqui"
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = "587"
SMTP_USER = "seu-email@gmail.com"
SMTP_PASSWORD = "sua-senha-de-app"
SMTP_FROM_NAME = "Samsung SMB"
```

7. Clique em **Deploy** 🚀

---

### Opção 2: Render (Grátis)

1. Crie uma conta em [render.com](https://render.com)
2. Crie um **New Web Service**
3. Conecte seu repositório do GitHub
4. Configure:
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `streamlit run streamlit_app.py --server.port $PORT --server.address 0.0.0.0`
5. Adicione as variáveis de ambiente em **Environment**
6. Clique em **Create Web Service**

---

### Opção 3: Railway (Grátis com limites)

1. Crie uma conta em [railway.app](https://railway.app)
2. Crie um **New Project** → Deploy from GitHub repo
3. Selecione seu repositório
4. O Railway detectará automaticamente o `requirements.txt`
5. Adicione as variáveis de ambiente em **Variables**
6. O deploy será feito automaticamente

---

## 🔐 Configuração do E-mail (SMTP)

O sistema pode enviar e-mails de confirmação automaticamente ao cliente após o cadastro de um atendimento.

### Gmail (Recomendado)

1. Ative a **verificação em duas etapas** na sua conta Google
2. Gere uma **Senha de App**:
   - Acesse: [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)
   - Selecione "Outro" → digite "Samsung SMB" → clique em "Gerar"
   - Copie a senha de 16 caracteres gerada
3. Configure nos Secrets:
   - `SMTP_USER`: seu-email@gmail.com
   - `SMTP_PASSWORD`: a senha de app de 16 caracteres

### Outros provedores

| Provedor | Host | Porta |
|---|---|---|
| Gmail | smtp.gmail.com | 587 |
| Outlook | smtp.office365.com | 587 |
| Yahoo | smtp.mail.yahoo.com | 587 |

---

## 📝 Nomenclaturas Utilizadas

O sistema utiliza as seguintes nomenclaturas nos campos:

| Campo | Descrição |
|---|---|
| **Nome Completo do Atendente** | Nome do responsável pelo atendimento |
| **Data do Atendimento** | Data em que o atendimento foi realizado |
| **Número do Pedido** | Código único de identificação do pedido |
| **Valor do Pedido** | Valor monetário total do atendimento |
| **Cadastrar Atendimento** | Botão de envio do formulário |

---

## 👤 Acesso Administrativo

Para acessar o painel administrativo (histórico e gráficos):

1. Clique na **seta no canto superior esquerdo** para abrir a barra lateral
2. Digite a **senha de administrador**
3. O painel administrativo será exibido com duas abas:
   - **📋 Histórico Completo**: Tabela com todos os atendimentos e exportação Excel
   - **📊 Dashboard de Análise**: Gráficos de atendimentos por atendente e por período

**Senha padrão**: `admin123` (altere via variável `ADMIN_PASSWORD`)

---

## 📊 Dashboard e Gráficos

O painel administrativo inclui:

### Gráficos de Barras
- **Atendimentos por Atendente**: Quantidade total de atendimentos de cada responsável
- **Valor por Atendente**: Faturamento total de cada atendente

### Gráficos de Linhas
- **Evolução de Atendimentos**: Quantidade de atendimentos ao longo do tempo
- **Evolução de Faturamento**: Valor total de pedidos ao longo do tempo

### Métricas na Página Inicial
- Total de atendimentos cadastrados
- Valor total acumulado
- Ticket médio (valor médio por atendimento)

---

## ⚙️ Variáveis de Ambiente

| Variável | Obrigatória | Descrição |
|---|---|---|
| `ADMIN_PASSWORD` | Sim | Senha de acesso à área administrativa |
| `SMTP_HOST` | Não | Servidor SMTP (padrão: smtp.gmail.com) |
| `SMTP_PORT` | Não | Porta SMTP (padrão: 587) |
| `SMTP_USER` | Não | Usuário/e-mail para autenticação SMTP |
| `SMTP_PASSWORD` | Não | Senha ou senha de app para SMTP |
| `SMTP_FROM_NAME` | Não | Nome do remetente nos e-mails |

---

## 🛠️ Tecnologias Utilizadas

- **Python 3.10+**
- **Streamlit** — Interface web
- **SQLite** — Banco de dados local
- **Pandas** — Manipulação de dados
- **OpenPyXL** — Exportação para Excel
- **smtplib** — Envio de e-mails

---

## 📄 Licença

Este projeto é de uso interno da equipe Samsung SMB.
