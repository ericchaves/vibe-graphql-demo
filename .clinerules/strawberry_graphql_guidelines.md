# Strawberry GraphQL Guidelines for GraphQL Filter Demo

This document outlines the guidelines for using the Strawberry library and implementing the GraphQL schema for the GraphQL Filter Demo project.

## Schema First Approach

*   Define the GraphQL schema using Strawberry's type hinting and decorators.
*   Prioritize clarity and maintainability in the schema definition.

## VisitaType Consolidation

*   The API will expose a single `VisitaType` that consolidates relevant fields from the `FatoVisitas` and all dimension tables.
*   Avoid exposing the underlying data warehouse structure directly to API consumers.

## InputFilter Implementation

*   Define generic `InputFilter` types for common data types (String, Int, DateTime, etc.).
*   Use these generic filters to build the `VisitaFilterInput`.
*   Ensure the filter logic in the backend correctly translates these filters to SQL `WHERE` clauses on the appropriate dimension table columns.

## Resolvers

*   Implement efficient resolvers for the `getVisitas` query.
*   The resolver should handle the database connection, SQL query construction (including necessary JOINs), and data mapping to `VisitaType`.
*   Optimize queries to minimize database calls, especially when fetching related dimension data.

## Error Handling

*   Implement proper error handling within resolvers.
*   Return meaningful GraphQL errors for issues like invalid input or database errors.

## Input Validation

*   Utilize Strawberry's features or implement custom logic for validating input arguments, especially in filters.

## Naming Conventions

*   Follow standard GraphQL naming conventions (PascalCase for types, camelCase for fields).
*   Align GraphQL field names with the consolidated `VisitaType` representation.
