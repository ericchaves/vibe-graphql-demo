# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
# (This section should be empty for now, as all previous additions are part of stage-7.0)

### Changed

### Deprecated

### Removed

### Fixed
- Resolved errors in `seed_data.py` related to incorrect primary key column name generation for dimension tables.
- Fixed SQL query construction in `schema.py` to prevent "You can only execute one statement at a time" error by removing a misplaced semicolon.
- Corrected table alias usage in `schema.py`'s `field_mapping` and filter condition builders to resolve "no such column" errors when applying GraphQL filters.

### Security

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
