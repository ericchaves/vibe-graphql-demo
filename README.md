# GraphQL Filter Demo

This project demonstrates the implementation of complex filtering in a GraphQL API using Python and Strawberry, backed by a SQLite data warehouse.

## Setup

To set up the development environment, it is highly recommended to use the provided Devcontainer with VS Code.

1.  **Clone the repository:**
    ```bash
    git clone <repository_url>
    cd graphql-filter-demo
    ```
2.  **Open in Devcontainer (Recommended):**
    *   If you have the VS Code Remote - Containers extension installed, VS Code should automatically prompt you to "Reopen in Container". Click this button.
    *   If not, open the Command Palette (Ctrl+Shift+P or Cmd+Shift+P), search for "Remote-Containers: Reopen in Container", and select it.
    *   The devcontainer comes with Python and `pip` pre-installed.

3.  **Dependency Management:**

    This project uses a hybrid approach for Python package management:

    *   **Inside the Devcontainer (Recommended):**
        *   Standard `pip` is used. The devcontainer environment is pre-configured.
        *   To install dependencies:
            ```bash
            pip install -r requirements.txt
            ```
        *   To add a new package:
            ```bash
            pip install <package_name>
            pip freeze > requirements.txt
            ```
    *   **Outside the Devcontainer (on the Host):**
        *   `uv` is recommended for creating and managing a virtual environment.
        *   Install `uv` if you haven't already (see [uv installation guide](https://github.com/astral-sh/uv#installation)).
        *   Create and activate a virtual environment:
            ```bash
            uv venv .venv
            source .venv/bin/activate  # For Linux/macOS
            # .venv\Scripts\Activate.ps1 # For Windows PowerShell
            # .venv\Scripts\activate.bat   # For Windows CMD
            ```
        *   Install dependencies:
            ```bash
            uv pip install -r requirements.txt
            ```
        *   To add a new package:
            ```bash
            uv pip install <package_name>
            uv pip freeze > requirements.txt
            ```
    *   The `postCreateCommand` in `.devcontainer/devcontainer.json` attempts to install dependencies using `pip` when the devcontainer is first built.

4.  **Initialize the Database:**
    *   If inside the devcontainer or if you have activated a virtual environment on the host:
    Run the initialization script to create the SQLite database and tables:
    ```bash
    python init_db.py
    ```
5.  **Seed Data (Optional but Recommended):**
    *   If inside the devcontainer or if you have activated a virtual environment on the host:
    Populate the database with example data for testing the API:
    ```bash
    python seed_data.py
    ```

## Running the Application

Once the development environment is set up (devcontainer or host venv) and the database is initialized, you can run the GraphQL API.

*   **Inside the Devcontainer or with `pip` on Host (in activated venv):**
    ```bash
    python -m uvicorn main:app --reload
    ```
*   **With `uv` on Host (in activated venv):**
    ```bash
    uvicorn main:app --reload
    ```

The API will be accessible at `http://localhost:8000`. You can also use the Makefile:

*   `make run-server`: Initializes the DB, seeds data, and starts the server.
*   `make test`: Runs all tests.

## API Overview

The GraphQL API provides a single query:

*   `getVisitas(filter: VisitaFilterInput): [VisitaType]`

This query allows fetching visit data with complex filtering capabilities using the `VisitaFilterInput`.

### `VisitaType`

The `VisitaType` consolidates relevant information from the `FatoVisitas` and all dimension tables, providing a simplified view for API consumers. It includes fields such as:

*   `idVisita`
*   `timestampVisita`
*   `nomeDominio`
*   `caminhoPagina`
*   `urlCompleta`
*   `nomeNavegador`
*   `soUsuarioNavegador`
*   `tipoDispositivo`
*   `enderecoIp`
*   `paisGeografia`
*   `tipoReferencia`
*   ... and other fields from the dimensions.

### `VisitaFilterInput`

The `VisitaFilterInput` allows filtering the `getVisitas` query based on various fields of the `VisitaType`. It utilizes generic `InputFilter` types (`StringFilterInput`, `IntFilterInput`, `DateTimeFilterInput`) for different data types to enable complex filtering operations.

**Supported Operations:**

*   **Common:** `equals`, `notEquals`, `In`, `notIn`
*   **String:** `contains`, `startsWith`, `endsWith`
*   **Int/DateTime:** `greaterThan`, `greaterThanOrEqual`, `lessThan`, `lessThanOrEqual`, `between`, `notBetween`
*   **Logical Combinators:** `AND`, `OR` (accept a list of `VisitaFilterInput` objects)

**Implicit Logic:**

*   Multiple conditions within a single field's filter input (e.g., `greaterThan` and `lessThan` for `timestampVisita`) are combined with `AND`.
*   Filters applied to different direct fields at the same level (e.g., `nomeDominio` and `tipoDispositivo`) are combined with `AND`.
*   If `AND` or `OR` fields are used at a level, they define the primary logic for combining the filters listed within them. Any direct field filters at the same level are implicitly `AND`ed with the result of the `AND`/`OR` block. For clarity, it's often best to nest all desired conditions within explicit `AND` or `OR` blocks.

**Examples:**

1.  **Simple Equality:** Find visits from "example.com".

```graphql
```graphql
query GetVisitasByDomain($filter: VisitaFilterInput) {
  getVisitas(filter: $filter) { idVisita nomeDominio }
}
# Variables
{ "filter": { "nomeDominio": { "equals": "example.com" } } }
```

2.  **Combined Direct Fields (Implicit AND):** Find visits from "example.com" on "Mobile" devices.
```graphql
query GetVisitasByDomainAndDevice($filter: VisitaFilterInput) {
  getVisitas(filter: $filter) { idVisita nomeDominio tipoDispositivo }
}
# Variables
{
  "filter": {
    "nomeDominio": { "equals": "example.com" },
    "tipoDispositivo": { "equals": "Mobile" }
  }
}
```

3.  **Using `between` for Timestamps:** Find visits between two specific times.
```graphql
query GetVisitasByTimestampBetween($filter: VisitaFilterInput) {
  getVisitas(filter: $filter) { idVisita timestampVisita }
}
# Variables
{
  "filter": {
    "timestampVisita": {
      "between": ["2023-01-01T09:00:00Z", "2023-01-01T11:00:00Z"]
    }
  }
}
```

4.  **Using `notBetween` for Integers:** Find visits not in years 2020-2022.
```graphql
query GetVisitasByAnoNotBetween($filter: VisitaFilterInput) {
  getVisitas(filter: $filter) { idVisita ano }
}
# Variables
{ "filter": { "ano": { "notBetween": [2020, 2022] } } }
```

5.  **Explicit `AND`:** Find visits from "example.com" AND using "Desktop".
```graphql
query GetVisitasExplicitAnd($filter: VisitaFilterInput) {
  getVisitas(filter: $filter) { idVisita nomeDominio tipoDispositivo }
}
# Variables
{
  "filter": {
    "AND": [
      { "nomeDominio": { "equals": "example.com" } },
      { "tipoDispositivo": { "equals": "Desktop" } }
    ]
  }
}
```

6.  **Explicit `OR`:** Find visits using "Chrome" OR "Firefox".
```graphql
query GetVisitasExplicitOr($filter: VisitaFilterInput) {
  getVisitas(filter: $filter) { idVisita nomeNavegador }
}
# Variables
{
  "filter": {
    "OR": [
      { "nomeNavegador": { "equals": "Chrome" } },
      { "nomeNavegador": { "equals": "Firefox" } }
    ]
  }
}
```

7.  **Nested Logic:** Find visits from "example.com" that are (from "USA" OR using "Chrome").
```graphql
query GetVisitasNested($filter: VisitaFilterInput) {
  getVisitas(filter: $filter) { idVisita nomeDominio paisGeografia nomeNavegador }
}
# Variables
{
  "filter": {
    "AND": [
      { "nomeDominio": { "equals": "example.com" } },
      {
        "OR": [
          { "paisGeografia": { "equals": "USA" } },
          { "nomeNavegador": { "equals": "Chrome" } }
        ]
      }
    ]
  }
}
```

8.  **Complex Combination:** Find visits that are ( (from "USA" AND "Mobile") OR (Browser="Chrome" AND Year between 2022-2023) ) AND occurred after 2023-01-01.
```graphql
query GetVisitasComplex($filter: VisitaFilterInput) {
  getVisitas(filter: $filter) { idVisita nomeDominio paisGeografia tipoDispositivo nomeNavegador ano timestampVisita }
}
# Variables
{
  "filter": {
    "timestampVisita": { "greaterThan": "2023-01-01T00:00:00Z" },
    "OR": [
      {
        "AND": [
          { "paisGeografia": { "equals": "USA" } },
          { "tipoDispositivo": { "equals": "Mobile" } }
        ]
      },
      {
        "AND": [
          { "nomeNavegador": { "equals": "Chrome" } },
          { "ano": { "between": [2022, 2023] } }
        ]
      }
    ]
  }
}
```

## Data Warehouse

The backend utilizes a SQLite database with a data warehouse structure. The core is the `FatoVisitas` table, linked to various dimension tables including:

*   `DimDominio`
*   `DimPagina`
*   `DimUrl`
*   `DimNavegador`
*   `DimUtm`
*   `DimSessao`
*   `DimDispositivo`
*   `DimIp`
*   `DimTempo`
*   `DimGeografia`
*   `DimReferencia`

The GraphQL API abstracts this structure, providing a consolidated view through the `VisitaType`.

## Project Workflow

This project follows the workflow guidelines outlined in the `.clinerules/project_workflow.md` file, including:

*   Maintaining a `changelog.md` for tracking changes.
*   Using a `tasks.md` checklist for task management.
*   Following conventions for Git commit messages.
*   Adhering to Python best practices (`.clinerules/python_best_practices.md`).
*   Following Strawberry GraphQL guidelines (`.clinerules/strawberry_graphql_guidelines.md`).
*   Adhering to SQLite data modeling guidelines (`.clinerules/sqlite_data_modeling.md`).
