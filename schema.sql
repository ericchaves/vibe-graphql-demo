-- SQLite schema for GraphQL Filter Demo Data Warehouse

-- Dimension Tables

CREATE TABLE DimDominio (
    id_dim_dominio INTEGER PRIMARY KEY AUTOINCREMENT,
    nome_dominio TEXT NOT NULL UNIQUE
);

CREATE TABLE DimPagina (
    id_dim_pagina INTEGER PRIMARY KEY AUTOINCREMENT,
    caminho_pagina TEXT NOT NULL UNIQUE
);

CREATE TABLE DimUrl (
    id_dim_url INTEGER PRIMARY KEY AUTOINCREMENT,
    url_completa TEXT NOT NULL UNIQUE
);

CREATE TABLE DimNavegador (
    id_dim_navegador INTEGER PRIMARY KEY AUTOINCREMENT,
    nome_navegador TEXT NOT NULL,
    versao_navegador TEXT,
    motor_renderizacao TEXT,
    sistema_operacional_usuario TEXT NOT NULL,
    UNIQUE (nome_navegador, versao_navegador, motor_renderizacao, sistema_operacional_usuario)
);

CREATE TABLE DimUtm (
    id_dim_utm INTEGER PRIMARY KEY AUTOINCREMENT,
    utm_source TEXT,
    utm_medium TEXT,
    utm_campaign TEXT,
    utm_term TEXT,
    utm_content TEXT,
    UNIQUE (utm_source, utm_medium, utm_campaign, utm_term, utm_content)
);

CREATE TABLE DimSessao (
    id_dim_sessao INTEGER PRIMARY KEY AUTOINCREMENT,
    id_usuario_sessao TEXT, -- Can be NULL if user is not logged in
    id_sessao_navegador TEXT NOT NULL UNIQUE
);

CREATE TABLE DimDispositivo (
    id_dim_dispositivo INTEGER PRIMARY KEY AUTOINCREMENT,
    tipo_dispositivo TEXT NOT NULL,
    marca_dispositivo TEXT,
    modelo_dispositivo TEXT,
    resolucao_tela TEXT,
    UNIQUE (tipo_dispositivo, marca_dispositivo, modelo_dispositivo, resolucao_tela)
);

CREATE TABLE DimIp (
    id_dim_ip INTEGER PRIMARY KEY AUTOINCREMENT,
    endereco_ip TEXT NOT NULL UNIQUE
);

CREATE TABLE DimTempo (
    id_dim_tempo INTEGER PRIMARY KEY AUTOINCREMENT,
    data_completa TEXT NOT NULL UNIQUE, -- YYYY-MM-DD HH:MM:SS format
    ano INTEGER NOT NULL,
    mes INTEGER NOT NULL,
    dia INTEGER NOT NULL,
    dia_semana INTEGER NOT NULL, -- 0 for Sunday, 6 for Saturday
    hora INTEGER NOT NULL,
    minuto INTEGER NOT NULL
);

CREATE TABLE DimGeografia (
    id_dim_geografia INTEGER PRIMARY KEY AUTOINCREMENT,
    pais TEXT,
    regiao TEXT,
    cidade TEXT,
    UNIQUE (pais, regiao, cidade)
);

CREATE TABLE DimReferencia (
    id_dim_referencia INTEGER PRIMARY KEY AUTOINCREMENT,
    url_referencia TEXT, -- Can be NULL for direct traffic
    tipo_referencia TEXT NOT NULL, -- Ex: Direct, Organic, Social, Paid
    UNIQUE (url_referencia, tipo_referencia)
);

-- Fact Table

CREATE TABLE FatoVisitas (
    id_visita INTEGER PRIMARY KEY AUTOINCREMENT,
    id_dim_dominio INTEGER NOT NULL,
    id_dim_pagina INTEGER NOT NULL,
    id_dim_url INTEGER NOT NULL,
    id_dim_navegador INTEGER NOT NULL,
    id_dim_utm INTEGER, -- Can be NULL if no UTM tags
    id_dim_sessao INTEGER NOT NULL,
    id_dim_dispositivo INTEGER NOT NULL,
    id_dim_ip INTEGER NOT NULL,
    id_dim_tempo INTEGER NOT NULL,
    id_dim_geografia INTEGER, -- Can be NULL if IP lookup fails
    id_dim_referencia INTEGER, -- Can be NULL for direct traffic
    timestamp_visita INTEGER NOT NULL, -- Unix timestamp

    FOREIGN KEY (id_dim_dominio) REFERENCES DimDominio(id_dim_dominio),
    FOREIGN KEY (id_dim_pagina) REFERENCES DimPagina(id_dim_pagina),
    FOREIGN KEY (id_dim_url) REFERENCES DimUrl(id_dim_url),
    FOREIGN KEY (id_dim_navegador) REFERENCES DimNavegador(id_dim_navegador),
    FOREIGN KEY (id_dim_utm) REFERENCES DimUtm(id_dim_utm),
    FOREIGN KEY (id_dim_sessao) REFERENCES DimSessao(id_dim_sessao),
    FOREIGN KEY (id_dim_dispositivo) REFERENCES DimDispositivo(id_dim_dispositivo),
    FOREIGN KEY (id_dim_ip) REFERENCES DimIp(id_dim_ip),
    FOREIGN KEY (id_dim_tempo) REFERENCES DimTempo(id_dim_tempo),
    FOREIGN KEY (id_dim_geografia) REFERENCES DimGeografia(id_dim_geografia),
    FOREIGN KEY (id_dim_referencia) REFERENCES DimReferencia(id_dim_referencia)
);

-- Indexes for performance on foreign keys in the fact table
CREATE INDEX idx_fato_dominio ON FatoVisitas (id_dim_dominio);
CREATE INDEX idx_fato_pagina ON FatoVisitas (id_dim_pagina);
CREATE INDEX idx_fato_url ON FatoVisitas (id_dim_url);
CREATE INDEX idx_fato_navegador ON FatoVisitas (id_dim_navegador);
CREATE INDEX idx_fato_utm ON FatoVisitas (id_dim_utm);
CREATE INDEX idx_fato_sessao ON FatoVisitas (id_dim_sessao);
CREATE INDEX idx_fato_dispositivo ON FatoVisitas (id_dim_dispositivo);
CREATE INDEX idx_fato_ip ON FatoVisitas (id_dim_ip);
CREATE INDEX idx_fato_tempo ON FatoVisitas (id_dim_tempo);
CREATE INDEX idx_fato_geografia ON FatoVisitas (id_dim_geografia);
CREATE INDEX idx_fato_referencia ON FatoVisitas (id_dim_referencia);
CREATE INDEX idx_fato_timestamp ON FatoVisitas (timestamp_visita);

-- Indexes for frequently queried dimension attributes
CREATE INDEX idx_dim_dominio_nome ON DimDominio (nome_dominio);
CREATE INDEX idx_dim_pagina_caminho ON DimPagina (caminho_pagina);
CREATE INDEX idx_dim_url_completa ON DimUrl (url_completa);
CREATE INDEX idx_dim_navegador_nome ON DimNavegador (nome_navegador);
CREATE INDEX idx_dim_navegador_so ON DimNavegador (sistema_operacional_usuario);
CREATE INDEX idx_dim_dispositivo_tipo ON DimDispositivo (tipo_dispositivo);
CREATE INDEX idx_dim_ip_endereco ON DimIp (endereco_ip);
CREATE INDEX idx_dim_tempo_data ON DimTempo (data_completa);
CREATE INDEX idx_dim_tempo_ano ON DimTempo (ano);
CREATE INDEX idx_dim_tempo_mes ON DimTempo (mes);
CREATE INDEX idx_dim_tempo_dia ON DimTempo (dia);
CREATE INDEX idx_dim_geografia_pais ON DimGeografia (pais);
CREATE INDEX idx_dim_geografia_cidade ON DimGeografia (cidade);
CREATE INDEX idx_dim_referencia_tipo ON DimReferencia (tipo_referencia);
