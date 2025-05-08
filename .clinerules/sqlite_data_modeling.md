# SQLite Data Modeling Guidelines for GraphQL Filter Demo

This document outlines the guidelines for data modeling using SQLite for the GraphQL Filter Demo project, focusing on the data warehouse structure.

## Adherence to DW Schema

*   Strictly follow the defined data warehouse schema with a central fact table (`FatoVisitas`) and associated dimension tables.
*   Ensure correct relationships and foreign keys are defined in the schema.

## SQLite Data Types

*   Use appropriate SQLite data types for each column (e.g., `INTEGER` for IDs and counts, `TEXT` for strings, `REAL` for floating-point numbers, `BLOB` for binary data, `INTEGER` for timestamps or dates stored as Unix time).
*   Be mindful of SQLite's flexible typing but aim for consistency.

## Primary and Foreign Keys

*   Define primary keys (`PRIMARY KEY`) for all tables.
*   Define foreign keys (`FOREIGN KEY`) to enforce relationships between the fact and dimension tables.
*   Consider using `INTEGER PRIMARY KEY` which is an alias for `ROWID` and can offer performance benefits.

## Indexing

*   Create indexes on columns frequently used in `WHERE` clauses or `JOIN` conditions, especially foreign key columns in the fact table.
*   Analyze query patterns to identify columns that would benefit from indexing.

## Normalization

*   Maintain a normalized structure for dimension tables to avoid data redundancy.
*   The fact table will naturally have foreign keys referencing the dimensions.

## Data Integrity

*   Utilize constraints (e.g., `NOT NULL`, `UNIQUE`) to ensure data integrity where appropriate.
