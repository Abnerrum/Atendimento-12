-- ═══════════════════════════════════════════════════════════════════════════
-- SETUP INICIAL — Sistema de Atendimentos Samsung SMB
-- Execute este script no MySQL Workbench antes de rodar a aplicação.
-- ═══════════════════════════════════════════════════════════════════════════

-- 1. Cria o banco (caso ainda não exista)
CREATE DATABASE IF NOT EXISTS samsung_smb
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE samsung_smb;

-- 2. Tabela de atendimentos (Pedido SMB)
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

-- 3. Tabela de pagamentos (Pedido Contigo)
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

-- 4. Tabela de vendedores
CREATE TABLE IF NOT EXISTS vendedores (
    id         INT          AUTO_INCREMENT PRIMARY KEY,
    nome       VARCHAR(150) NOT NULL UNIQUE,
    criado_em  VARCHAR(30)  DEFAULT ''
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 5. Tabela de notificações
CREATE TABLE IF NOT EXISTS notificacoes (
    id               INT          AUTO_INCREMENT PRIMARY KEY,
    tipo             VARCHAR(30)  NOT NULL,
    destinatario     VARCHAR(200) NOT NULL,
    assunto          VARCHAR(300) DEFAULT '',
    mensagem         TEXT         DEFAULT '',
    status           VARCHAR(30)  DEFAULT 'enviada',
    data_hora_envio  VARCHAR(30)  DEFAULT '',
    referencia_id    INT          DEFAULT NULL,
    referencia_tipo  VARCHAR(50)  DEFAULT NULL,
    lido             TINYINT(1)   DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 6. Tabela de preferências de notificação por usuário
CREATE TABLE IF NOT EXISTS preferencias_notificacao (
    id                INT          AUTO_INCREMENT PRIMARY KEY,
    usuario           VARCHAR(150) NOT NULL UNIQUE,
    email_atendimento TINYINT(1)   DEFAULT 1,
    email_pagamento   TINYINT(1)   DEFAULT 1,
    notif_sistema     TINYINT(1)   DEFAULT 1,
    criada_em         VARCHAR(30)  DEFAULT ''
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ═══════════════════════════════════════════════════════════════════════════
-- OPCIONAL: crie um usuário dedicado em vez de usar root
-- ═══════════════════════════════════════════════════════════════════════════
-- CREATE USER IF NOT EXISTS 'smb_user'@'localhost' IDENTIFIED BY 'senha_forte';
-- GRANT ALL PRIVILEGES ON samsung_smb.* TO 'smb_user'@'localhost';
-- FLUSH PRIVILEGES;

select*from vendedores;
select*from pagamentos;
select*from Atendimentos;