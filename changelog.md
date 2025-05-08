# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- `httpx` dependency to `requirements.txt` for `fastapi.testclient`.

### Changed
- Revised `Makefile` to conditionally activate virtual environment. It now checks for `REMOTE_CONTAINERS` environment variable to skip venv activation if running inside a devcontainer.
- Updated `tests/test_query_builder.py` to use table aliases (e.g., `dd.nome_dominio`) instead of full table names in assertions to match actual query builder output.
- Modified `tests/test_graphql_api.py` in `test_get_visitas_filter_by_timestamp_range` to correctly parse ISO string timestamps returned by the API.

### Deprecated

### Removed

### Fixed
- Corrected and completed the `test_get_visitas_filter_by_timestamp_range` test in `tests/test_graphql_api.py`.
- Ensured all tests pass by running them with `uv run python -m unittest discover -s tests -v`.
- Resolved initial test execution failures by installing dependencies with `uv pip install -r requirements.txt` and running tests within the `uv` managed environment.
- Resolved errors in `seed_data.py` related to incorrect primary key column name generation for dimension tables.
- Fixed SQL query construction in `schema.py` to prevent "You can only execute one statement at a time" error by removing a misplaced semicolon.
- Corrected table alias usage in `schema.py`'s `field_mapping` and filter condition builders to resolve "no such column" errors when applying GraphQL filters.


### Security

## [stage-9.0] - 2025-05-08

### Added
- Created `Makefile` with targets for `test` (run tests), `run-server` (initialize DB, seed data, run server), and `clean` (Etapa 9).
- Updated `tasks.md` and `changelog.md` to reflect completion of Etapa 9.

## [stage-7.0] - 2025-05-08

### Added
- Initial project setup and configuration (Etapa 0).
- Database modeling and creation script (Etapa 1).
- Defined GraphQL types with Strawberry (Etapa 2), including consolidated `VisitaType` and `InputFilter` types.
- Implemented GraphQL resolvers (Etapa 3), including database interaction and dynamic query building with filters.
- Created script for generating and inserting example data (Etapa 4).
- Implemented backend filtering logic (Etapa 5), translating InputFilters to SQL WHERE clauses.
- Added unit and integration tests (Etapa 6) for query building and GraphQL API.
- Completed final documentation (Etapa 7), including expanded README and API documentation.
