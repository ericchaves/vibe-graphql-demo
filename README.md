# GraphQL Filter Demo

This project demonstrates the implementation of complex filtering in a GraphQL API using Python and Strawberry, backed by a SQLite data warehouse.

## Setup

To set up the development environment, it is highly recommended to use the provided Devcontainer with VS Code.

1.  **Clone the repository:**
    ```bash
    git clone <repository_url>
    cd graphql-filter-demo
    ```
2.  **Open in Devcontainer:**
    *   If you have the VS Code Remote - Containers extension installed, VS Code should automatically prompt you to "Reopen in Container". Click this button.
    *   If not, open the Command Palette (Ctrl+Shift+P or Cmd+Shift+P), search for "Remote-Containers: Reopen in Container", and select it.
3.  **Set up Virtual Environment and Install Dependencies:**
    *   This project uses `uv` for Python package management.
    *   Ensure you are inside the project directory (`graphql-filter-demo`).
    *   Install the required Python packages from `requirements.txt`:
        ```bash
        uv pip install -r requirements.txt
        ```
    *   Note: The `postCreateCommand` in `.devcontainer/devcontainer.json` also attempts to install dependencies when the devcontainer is first built. The steps above ensure you can manually set up or update the environment.

4.  **Initialize the Database:** Run the initialization script to create the SQLite database and tables:
    ```bash
    python init_db.py
    ```
5.  **Seed Data (Optional but Recommended):** Populate the database with example data for testing the API:
    ```bash
    python seed_data.py
    ```

## Running the Application

Once the Devcontainer is set up and the database is initialized, you can run the GraphQL API using Uvicorn:

```bash
uvicorn main:app --reload
```

The API will be accessible at `http://localhost:8000`.

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

The `VisitaFilterInput` allows filtering the `getVisitas` query based on various fields of the `VisitaType`. It utilizes generic `InputFilter` types for different data types (String, Int, DateTime) to enable complex filtering operations like equality, inequality, containment, range checks, and list inclusion/exclusion.

Example Query with Filter:

```graphql
query GetVisitasByDomainAndDevice($filter: VisitaFilterInput) {
  getVisitas(filter: $filter) {
    idVisita
    nomeDominio
    tipoDispositivo
    nomeNavegador
  }
}

# Query Variables
{
  "filter": {
    "nomeDominio": {
      "equals": "example.com"
    },
    "tipoDispositivo": {
      "equals": "Mobile"
    }
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
