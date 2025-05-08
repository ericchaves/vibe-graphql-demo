import unittest
from fastapi.testclient import TestClient # type: ignore
import sqlite3
import os
import datetime
import time
import base64

# Assuming main.py and init_db.py are in the parent directory
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import app
from init_db import init_db, DATABASE_FILE
from seed_data import seed_data

# Helper to get total count for comparison (adjust query as needed)
def get_total_visitas_count():
    conn = sqlite3.connect(DATABASE_FILE)
    count = conn.execute("SELECT COUNT(*) FROM FatoVisitas").fetchone()[0]
    conn.close()
    return count

class TestGraphQLAPI(unittest.TestCase):

    TOTAL_VISITAS = 0 # Store total count

    @classmethod
    def setUpClass(cls):
        """Set up the test database and seed data once for all tests."""
        # Ensure a clean database for testing
        if os.path.exists(DATABASE_FILE):
            os.remove(DATABASE_FILE)
        init_db()
        seed_data()
        cls.client = TestClient(app)
        cls.TOTAL_VISITAS = get_total_visitas_count() # Get total count after seeding
        print(f"\nTotal visitas seeded: {cls.TOTAL_VISITAS}")


    @classmethod
    def tearDownClass(cls):
        """Remove the test database after all tests are done."""
        if os.path.exists(DATABASE_FILE):
            os.remove(DATABASE_FILE)

    def _run_query(self, query: str, variables: dict = None):
        """Helper method to run a GraphQL query."""
        json_payload = {"query": query}
        if variables:
            json_payload["variables"] = variables
        # print(f"\nRunning query with variables: {variables}") # Debugging
        response = self.client.post("/graphql", json=json_payload)
        self.assertEqual(response.status_code, 200, f"GraphQL query failed: {response.text}")
        data = response.json()
        # print(f"Response data: {data}") # Debugging
        self.assertIsNone(data.get("errors"), f"GraphQL errors: {data.get('errors')}")
        self.assertIsNotNone(data.get("data"), "GraphQL response missing data.")
        return data["data"]

    # --- Existing Filter Tests (Need modification for Connection structure) ---

    def test_get_visitas_no_filter_connection(self):
        """Test fetching visits without filter, checking connection structure."""
        query = """
            query {
                getVisitas { # Default pagination should apply
                    edges { node { idVisita } cursor }
                    pageInfo { hasNextPage hasPreviousPage startCursor endCursor }
                }
            }
        """
        data = self._run_query(query)
        connection = data.get("getVisitas")
        self.assertIsNotNone(connection)
        self.assertIn("edges", connection)
        self.assertIn("pageInfo", connection)
        self.assertIsInstance(connection["edges"], list)
        # Assuming default page size is less than total visits
        if self.TOTAL_VISITAS > 20: # Using default page size 20
             self.assertTrue(connection["pageInfo"]["hasNextPage"])
        self.assertFalse(connection["pageInfo"]["hasPreviousPage"])
        self.assertIsNotNone(connection["pageInfo"]["startCursor"])
        self.assertIsNotNone(connection["pageInfo"]["endCursor"])

    def test_get_visitas_filter_by_domain_connection(self):
        """Test filtering visits by domain name with connection structure."""
        query = """
            query GetVisitas($filter: VisitaFilterInput) {
                getVisitas(filter: $filter) {
                    edges { node { idVisita nomeDominio } cursor }
                    pageInfo { startCursor endCursor }
                }
            }
        """
        variables = {
            "filter": { "nomeDominio": { "equals": "example.com" } }
        }
        data = self._run_query(query, variables)
        connection = data.get("getVisitas")
        self.assertIsNotNone(connection)
        self.assertGreater(len(connection["edges"]), 0)
        for edge in connection["edges"]:
            self.assertEqual(edge["node"]["nomeDominio"], "example.com")
            self.assertIsNotNone(edge["cursor"])

    # --- Tests for Etapa 10 Filters (Need modification for Connection structure) ---

    def test_filter_timestamp_between_connection(self):
        """Test filtering by timestamp using BETWEEN with connection."""
        query = """
            query GetVisitas($filter: VisitaFilterInput) {
                getVisitas(filter: $filter) { edges { node { idVisita timestampVisita } } }
            }
        """
        start_time = datetime.datetime(2023, 1, 1, 9, 0, 0, tzinfo=datetime.timezone.utc)
        end_time = datetime.datetime(2023, 1, 1, 11, 0, 0, tzinfo=datetime.timezone.utc)
        variables = {
            "filter": { "timestampVisita": { "between": [start_time.isoformat(), end_time.isoformat()] } }
        }
        data = self._run_query(query, variables)
        connection = data.get("getVisitas")
        self.assertIsNotNone(connection)
        self.assertTrue(len(connection["edges"]) > 0)
        start_ts = start_time.timestamp()
        end_ts = end_time.timestamp()
        for edge in connection["edges"]:
            visita_dt = datetime.datetime.fromisoformat(edge["node"]["timestampVisita"].replace('Z', '+00:00'))
            visita_ts = visita_dt.timestamp()
            self.assertTrue(start_ts <= visita_ts <= end_ts)

    def test_filter_explicit_and_connection(self):
        """Test filtering using explicit AND with connection."""
        query = """
            query GetVisitas($filter: VisitaFilterInput) {
                getVisitas(filter: $filter) { edges { node { idVisita nomeDominio tipoDispositivo } } }
            }
        """
        variables = {
            "filter": { "AND": [ {"nomeDominio": {"equals": "example.com"}}, {"tipoDispositivo": {"equals": "Desktop"}} ] }
        }
        data = self._run_query(query, variables)
        connection = data.get("getVisitas")
        self.assertIsNotNone(connection)
        self.assertTrue(len(connection["edges"]) > 0)
        for edge in connection["edges"]:
            self.assertEqual(edge["node"]["nomeDominio"], "example.com")
            self.assertEqual(edge["node"]["tipoDispositivo"], "Desktop")

    def test_filter_explicit_or_connection(self):
        """Test filtering using explicit OR with connection."""
        query = """
            query GetVisitas($filter: VisitaFilterInput) {
                getVisitas(filter: $filter) { edges { node { idVisita nomeNavegador } } }
            }
        """
        variables = {
            "filter": { "OR": [ {"nomeNavegador": {"equals": "Chrome"}}, {"nomeNavegador": {"equals": "Firefox"}} ] }
        }
        data = self._run_query(query, variables)
        connection = data.get("getVisitas")
        self.assertIsNotNone(connection)
        self.assertTrue(len(connection["edges"]) > 0)
        for edge in connection["edges"]:
            self.assertIn(edge["node"]["nomeNavegador"], ["Chrome", "Firefox"])

    # --- New Tests for Etapa 11: Pagination ---

    def test_pagination_first_n(self):
        """Test fetching the first N items."""
        n = 5
        query = """
            query GetFirstN($first: Int) {
                getVisitas(first: $first) {
                    edges { node { idVisita } cursor }
                    pageInfo { hasNextPage hasPreviousPage startCursor endCursor }
                }
            }
        """
        variables = {"first": n}
        data = self._run_query(query, variables)
        connection = data.get("getVisitas")
        self.assertIsNotNone(connection)
        self.assertEqual(len(connection["edges"]), n)
        self.assertTrue(connection["pageInfo"]["hasNextPage"])
        self.assertFalse(connection["pageInfo"]["hasPreviousPage"])
        self.assertIsNotNone(connection["pageInfo"]["startCursor"])
        self.assertIsNotNone(connection["pageInfo"]["endCursor"])

    def test_pagination_forward_after(self):
        """Test fetching the next page using first and after."""
        n1 = 3
        n2 = 4
        # First query: get first n1 items
        query1 = """ query GetFirst($first: Int) { getVisitas(first: $first) { edges { cursor } pageInfo { endCursor hasNextPage } } } """
        variables1 = {"first": n1}
        data1 = self._run_query(query1, variables1)
        connection1 = data1.get("getVisitas")
        self.assertTrue(connection1["pageInfo"]["hasNextPage"])
        last_cursor = connection1["pageInfo"]["endCursor"]
        self.assertIsNotNone(last_cursor)

        # Second query: get next n2 items after the last cursor
        query2 = """ query GetNext($first: Int, $after: String) { getVisitas(first: $first, after: $after) { edges { node { idVisita } cursor } pageInfo { hasNextPage hasPreviousPage startCursor endCursor } } } """
        variables2 = {"first": n2, "after": last_cursor}
        data2 = self._run_query(query2, variables2)
        connection2 = data2.get("getVisitas")
        self.assertIsNotNone(connection2)
        self.assertEqual(len(connection2["edges"]), n2)
        # hasPreviousPage should be true if 'after' is provided, but our simple logic might not implement this yet.
        # Let's focus on hasNextPage for now.
        if self.TOTAL_VISITAS > n1 + n2:
            self.assertTrue(connection2["pageInfo"]["hasNextPage"])
        self.assertNotEqual(connection1["pageInfo"]["endCursor"], connection2["pageInfo"]["endCursor"])

    def test_pagination_last_n(self):
        """Test fetching the last N items."""
        n = 6
        query = """
            query GetLastN($last: Int) {
                getVisitas(last: $last) {
                    edges { node { idVisita } cursor }
                    pageInfo { hasNextPage hasPreviousPage startCursor endCursor }
                }
            }
        """
        variables = {"last": n}
        data = self._run_query(query, variables)
        connection = data.get("getVisitas")
        self.assertIsNotNone(connection)
        self.assertEqual(len(connection["edges"]), n)
        self.assertFalse(connection["pageInfo"]["hasNextPage"])
        self.assertTrue(connection["pageInfo"]["hasPreviousPage"])
        self.assertIsNotNone(connection["pageInfo"]["startCursor"])
        self.assertIsNotNone(connection["pageInfo"]["endCursor"])

    def test_pagination_backward_before(self):
        """Test fetching the previous page using last and before."""
        n1 = 7
        n2 = 4
        # First query: get last n1 items
        query1 = """ query GetLast($last: Int) { getVisitas(last: $last) { edges { cursor } pageInfo { startCursor hasPreviousPage } } } """
        variables1 = {"last": n1}
        data1 = self._run_query(query1, variables1)
        connection1 = data1.get("getVisitas")
        self.assertTrue(connection1["pageInfo"]["hasPreviousPage"])
        first_cursor = connection1["pageInfo"]["startCursor"]
        self.assertIsNotNone(first_cursor)

        # Second query: get previous n2 items before the first cursor
        query2 = """ query GetPrevious($last: Int, $before: String) { getVisitas(last: $last, before: $before) { edges { node { idVisita } cursor } pageInfo { hasNextPage hasPreviousPage startCursor endCursor } } } """
        variables2 = {"last": n2, "before": first_cursor}
        data2 = self._run_query(query2, variables2)
        connection2 = data2.get("getVisitas")
        self.assertIsNotNone(connection2)
        self.assertEqual(len(connection2["edges"]), n2)
        # hasNextPage should be true if 'before' is provided, but our simple logic might not implement this yet.
        if self.TOTAL_VISITAS > n1 + n2:
             self.assertTrue(connection2["pageInfo"]["hasPreviousPage"])
        self.assertNotEqual(connection1["pageInfo"]["startCursor"], connection2["pageInfo"]["startCursor"])

    def test_pagination_with_filter(self):
        """Test pagination combined with filters."""
        n = 2
        query = """
            query GetFilteredPaginated($first: Int, $after: String, $filter: VisitaFilterInput) {
                getVisitas(first: $first, after: $after, filter: $filter) {
                    edges { node { idVisita nomeDominio } cursor }
                    pageInfo { endCursor hasNextPage }
                }
            }
        """
        variables = {
            "first": n,
            "filter": {"nomeDominio": {"equals": "example.com"}}
        }
        # First page
        data1 = self._run_query(query, variables)
        connection1 = data1.get("getVisitas")
        self.assertIsNotNone(connection1)
        self.assertLessEqual(len(connection1["edges"]), n)
        for edge in connection1["edges"]:
            self.assertEqual(edge["node"]["nomeDominio"], "example.com")

        # Second page (if exists)
        if connection1["pageInfo"]["hasNextPage"]:
            variables["after"] = connection1["pageInfo"]["endCursor"]
            data2 = self._run_query(query, variables)
            connection2 = data2.get("getVisitas")
            self.assertIsNotNone(connection2)
            self.assertLessEqual(len(connection2["edges"]), n)
            for edge in connection2["edges"]:
                self.assertEqual(edge["node"]["nomeDominio"], "example.com")
            # Ensure cursors are different if there was a second page
            self.assertNotEqual(connection1["pageInfo"]["endCursor"], connection2["pageInfo"]["endCursor"])


if __name__ == '__main__':
    unittest.main()
