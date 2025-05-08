# Project Tasks

This document tracks the planned and completed tasks for the GraphQL Filter Demo project.

- [x] Etapa 0: Setup Inicial e Configuração do Projeto
    - [x] 0.1. Inicialização do Repositório Git (`git init`)
    - [x] 0.2. Configuração do Devcontainer (VS Code)
    - [x] 0.3. Criação da Estrutura de Diretrizes (`.clinerules`)
        - [x] Criar `.clinerules/python_best_practices.md`
        - [x] Criar `.clinerules/strawberry_graphql_guidelines.md`
        - [x] Criar `.clinerules/sqlite_data_modeling.md`
        - [x] Criar `.clinerules/project_workflow.md`
    - [x] 0.4. Criação dos Arquivos de Gerenciamento do Projeto
        - [x] Criar `changelog.md`
        - [x] Criar `tasks.md` (Esta tarefa será marcada como concluída após a criação deste arquivo)
        - [x] Criar `README.md` inicial
    - [x] 0.5. Criação do `.gitignore`

- [x] Etapa 1: Modelagem e Criação do Banco de Dados SQLite
    - [x] Gerar o script SQL (`schema.sql`)
    - [x] Criar um script Python (`init_db.py`) para inicializar o banco de dados
    - [x] Atualizar `tasks.md` e `changelog.md`

- [x] Etapa 2: Definição dos Tipos GraphQL com Strawberry (Visão Consolidada)
    - [x] Criar o tipo principal `VisitaType`
    - [x] Definir `InputFilter` types genéricos
    - [x] Definir `VisitaFilterInput`
    - [x] Atualizar `tasks.md` e `changelog.md`

- [x] Etapa 3: Implementação dos Resolvers GraphQL
    - [x] Criar a query `getVisitas`
    - [x] Implementar a lógica do resolver (conexão DB, construção SQL com JOINs, aplicação de filtros, mapeamento)
    - [x] Atualizar `tasks.md` e `changelog.md`

- [x] Etapa 4: Criação de Dados de Exemplo (Seed Data)
    - [x] Desenvolver um script Python (`seed_data.py`)
    - [x] Atualizar `tasks.md` e `changelog.md`

- [x] Etapa 5: Implementação da Lógica de Filtragem no Backend
    - [x] Traduzir `InputFilter` para cláusulas SQL `WHERE`
    - [x] Garantir tratamento de múltiplos filtros
    - [x] Atualizar `tasks.md` e `changelog.md`

- [x] Etapa 6: Testes
    - [x] Escrever testes unitários para construção de query SQL
    - [x] Escrever testes de integração para a API GraphQL
    - [x] Atualizar `tasks.md` e `changelog.md`

- [x] Etapa 7: Documentação Final
    - [x] Expandir o `README.md`
    - [x] Garantir documentação da API GraphQL acessível
    - [x] Atualizar `tasks.md` e `changelog.md`
