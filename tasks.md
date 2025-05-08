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

- [x] Etapa 8: Validação e Correção de Testes (Adicionado Pós-Etapa 6)
    - [x] Validar que todos os testes existentes estão corretos e rodando
    - [x] Corrigir `test_get_visitas_filter_by_timestamp_range` em `tests/test_graphql_api.py`
    - [x] Corrigir falhas em `tests/test_query_builder.py` devido a aliases de tabela
    - [x] Adicionar `httpx` como dependência e atualizar `requirements.txt`
    - [x] Garantir que todos os testes passem usando `uv run python -m unittest discover -s tests -v`
    - [x] Atualizar `tasks.md` (esta tarefa)

- [x] Etapa 9: Criação do Makefile
    - [x] Criar um `Makefile` com targets para:
        - [x] Rodar testes (`make test`)
        - [x] Rodar o servidor (`make run-server`)
            - [x] A task `run-server` deve inicializar o banco de dados (`init_db.py`)
            - [x] A task `run-server` deve alimentar os dados de seed (`seed_data.py`)
    - [x] Atualizar `tasks.md` e `changelog.md` (após a criação do Makefile)

- [x] Etapa 10: Melhorias Avançadas de Filtragem, Testes e Documentação
    - [x] 10.1. Modificar `IntFilterInput` e `DateTimeFilterInput` em `schema.py` para incluir operações `between` e `notBetween`.
    - [x] 10.2. Revisar `VisitaFilterInput` em `schema.py` para adicionar campos `AND` e `OR` para lógica combinada.
    - [x] 10.3. Atualizar a lógica de construção de query SQL em `schema.py` para suportar `BETWEEN`, `NOT BETWEEN`, `AND` e `OR`.
    - [x] 10.4. Desenvolver novos testes unitários em `tests/test_query_builder.py` para as novas operações e lógicas de filtro.
    - [x] 10.5. Desenvolver novos testes de integração em `tests/test_graphql_api.py` para as novas funcionalidades de filtro.
    - [x] 10.6. Atualizar `README.md` com exemplos práticos das novas operações de filtro (`BETWEEN`, `NOT BETWEEN`, `AND`, `OR`) e combinações.
    - [x] 10.7. Atualizar `changelog.md` com as mudanças da Etapa 10.
    - [x] 10.8. Criar tag Git `stage-10.0` e notas de release no `changelog.md` após conclusão e validação.

- [x] Etapa 11: Implementação de Paginação (Relay Cursor Connections)
    - [x] 11.1. Definir tipos `PageInfo`, `VisitaEdge`, `VisitaConnection` em `schema.py`.
    - [x] 11.2. Modificar query `getVisitas` em `schema.py` para aceitar argumentos de paginação (`first`, `after`, `last`, `before`) e retornar `VisitaConnection`.
    - [x] 11.3. Implementar lógica de paginação baseada em cursor no resolver `getVisitas` em `schema.py` (incluindo validação, codificação/decodificação de cursor, modificação da query SQL, processamento de resultados).
    - [x] 11.4. Adicionar testes de integração em `tests/test_graphql_api.py` para validar a paginação (forward, backward, com filtros, casos de borda).
    - [x] 11.5. Atualizar `README.md` para documentar a paginação (argumentos, tipo de retorno, exemplos).
    - [x] 11.6. Atualizar `changelog.md` com as mudanças da Etapa 11.
    - [x] 11.7. Criar tag Git `stage-11.0` e notas de release no `changelog.md` após conclusão e validação.

- [x] Etapa 12: Paginação Híbrida (Cursor e Offset) e Contagem Total
    - [x] 12.1. Adicionar argumentos `limit` e `offset` à query `getVisitas` em `schema.py`.
    - [x] 12.2. Adicionar campo `totalCount` ao tipo `VisitaConnection` em `schema.py`.
    - [x] 12.3. Implementar validação de argumentos conflitantes (cursor vs offset) no resolver `getVisitas`.
    - [x] 12.4. Implementar lógica de detecção de modo (cursor, offset, default) no resolver `getVisitas`.
    - [x] 12.5. Implementar cálculo de `totalCount` (query `COUNT(*)` separada com filtros).
    - [x] 12.6. Implementar construção condicional de query SQL (cursor vs offset/limit) no resolver.
    - [x] 12.7. Implementar processamento condicional de resultados (cursor vs offset) para `PageInfo` e `edges`.
    - [x] 12.8. Adicionar testes de integração em `tests/test_graphql_api.py` para offset, default, `totalCount`, e conflitos de argumentos.
    - [x] 12.9. Atualizar `README.md` para documentar a paginação híbrida, `totalCount`, e regras de validação.
    - [x] 12.10. Atualizar `changelog.md` com as mudanças da Etapa 12.
    - [x] 12.11. Criar tag Git `stage-12.0` e notas de release no `changelog.md` após conclusão e validação.

- [x] Etapa 13: Refatorar Paginação `getVisitas` com Input Types
    - [x] 13.1. Definir `CursorModeInput` e `PaginationModeInput` em `schema.py`.
    - [x] 13.2. Modificar `get_visitas` para usar `cursorArgs` e `offsetArgs` em `schema.py`.
    - [x] 13.3. Atualizar testes em `tests/test_graphql_api.py` para usar os novos input types.
    - [x] 13.4. Atualizar `README.md` com a nova assinatura e exemplos de paginação.
    - [x] 13.5. Atualizar `tasks.md` (esta tarefa).
