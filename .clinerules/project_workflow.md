# Project Workflow Guidelines for GraphQL Filter Demo

This document outlines the workflow and practices to be followed during the development of the GraphQL Filter Demo project.

⚠️ CRITICAL: DO NOT USE attempt_completion BEFORE TESTING ⚠️
⚠️ CRITICAL: DO NOT USE browse_action. ASK USER TO BROWSE AND REPORT THE RESULTS ⚠️
⚠️ CRITICAL: NEVER PERFORM A PUSH TO REMOTE REPOSITORY ⚠️

## Changelog Management

*   Maintain a `changelog.md` file at the root of the project.
*   Record all significant changes, new features, bug fixes, and breaking changes.
*   Follow a consistent format (e.g., "Keep a Changelog" format is recommended).
*   Update the changelog as part of the completion of each major task or before creating a new release/tag.

## Task Tracking

*   Maintain a `tasks.md` file at the root of the project.
*   List all planned development tasks using a checklist format (e.g., `- [ ] Task description`).
*   Mark tasks as completed by changing `[ ]` to `[x]`.
*   Refer to this file to understand the current progress and remaining work.

## Git Commit Messages

*   Write clear, concise, and descriptive Git commit messages.
*   Use the imperative mood in the subject line (e.g., "Add feature X", "Fix bug Y").
*   Include a body in the commit message for more detailed explanations if necessary.
*   Perform a commit after completing every task with a subsequent successfull code execution.
*   After completing a stage from the `tasks.md` and its child tasks, Use the `git tag` command to create a taf with the stage number (e.g., `stage-1.0`) and a corresponding release note in the `changelog.md`.

## Testing

*   For every feature developed, write unit and behavioral tests to validate its functionality as planned.
*   Tests must be executed whenever the code is changed to ensure no regressions are introduced.
*   Tests should be reviewed and updated throughout the development process to reflect any changes in requirements or implementation.

## README.md

*   Maintain a comprehensive `README.md` file at the root of the project.
*   Include instructions on setting up the development environment (using the devcontainer), installing dependencies, running the application, and a brief overview of the project and API.
*   Keep the README updated as the project evolves.

## Iterative Development

*   Follow the planned development stages.
*   Complete tasks incrementally, ensuring each step is stable before moving to the next.
*   Utilize the provided tools effectively to accomplish tasks.

## Key Considerations

- Only run and test the code inside a the devcontainer.

## Dependency Management

This project uses a hybrid approach for Python package management:
*   **Inside the Devcontainer:** Standard `pip` is used for managing dependencies. The devcontainer environment is pre-configured with Python and `pip`.
*   **Outside the Devcontainer (on the Host):** `uv` is recommended for creating and managing a virtual environment and installing dependencies.

### Inside the Devcontainer (using `pip`)

*   The devcontainer comes with Python and `pip` ready to use. No separate virtual environment activation is typically needed as the container itself provides isolation.
*   **Managing Dependencies:**
    *   **Installing from `requirements.txt`:** `pip install -r requirements.txt`
    *   **Adding a new package:** `pip install <package_name>`
    *   **Updating a package:** `pip install --upgrade <package_name>`
*   **Maintaining `requirements.txt`:**
    *   **Crucial:** After adding, removing, or updating any package, **immediately** update the `requirements.txt` file using: `pip freeze > requirements.txt`
    *   This ensures that the `requirements.txt` file always reflects the exact state of the project's dependencies.

### Outside the Devcontainer (on the Host, using `uv`)

*   `uv` is a fast Python package installer and resolver.
*   **Installation of `uv`:** Follow the official `uv` installation guide if not already installed.
*   **Creating a Virtual Environment (Recommended):**
    *   `uv venv .venv` (Creates a virtual environment in a `.venv` directory)
    *   Activate the environment:
        *   Linux/macOS: `source .venv/bin/activate`
        *   Windows (PowerShell): `.venv\Scripts\Activate.ps1`
        *   Windows (CMD): `.venv\Scripts\activate.bat`
*   **Managing Dependencies (with `uv` in an activated venv):**
    *   **Installing from `requirements.txt`:** `uv pip install -r requirements.txt`
    *   **Adding a new package:** `uv pip install <package_name>`
    *   **Updating a package:** `uv pip install --upgrade <package_name>`
*   **Maintaining `requirements.txt` (with `uv` in an activated venv):**
    *   **Crucial:** After adding, removing, or updating any package, **immediately** update the `requirements.txt` file using: `uv pip freeze > requirements.txt`
    *   This ensures that the `requirements.txt` file always reflects the exact state of the project's dependencies.
*   **Important:** When working outside the devcontainer, always ensure your `uv` commands are run within the activated virtual environment.
