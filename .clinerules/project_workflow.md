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