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
from schema import DEFAULT_PAGE_SIZE # Import default page size

# Helper to get total count for comparison (adjust query as needed)
def get_total_visitas_count(filter_dict=None):
    # This helper might need to become more sophisticated if we want to test
    # totalCount with filters applied directly via SQL, but for now,
    # we can test the GraphQL totalCount field itself.
    conn = sqlite3.connect(DATABASE_FILE)
    # Simple total count for now
    # TODO: Enhance this helper if needed to apply filters for more precise test setup
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

    def _run_query(self, query: str, variables: dict = None, expect_error: bool = False):
        """Helper method to run a GraphQL query, optionally expecting errors."""
        json_payload = {"query": query}
        if variables:
            json_payload["variables"] = variables
        # print(f"\nRunning query with variables: {variables}") # Debugging
        response = self.client.post("/graphql", json=json_payload)
        self.assertEqual(response.status_code, 200, f"GraphQL query failed: {response.text}")
        data = response.json()
        # print(f"Response data: {data}") # Debugging
        if expect_error:
            self.assertIsNotNone(data.get("errors"), "Expected GraphQL errors, but none found.")
            return None # Return None when errors are expected and found
        else:
            self.assertIsNone(data.get("errors"), f"GraphQL errors: {data.get('errors')}")
            self.assertIsNotNone(data.get("data"), "GraphQL response missing data.")
            return data["data"]

    # --- Existing Filter Tests (Modified for Connection structure) ---

    def test_get_visitas_no_filter_connection(self):
        """Test fetching visits without filter, checking connection structure and totalCount."""
        query = """
            query {
                getVisitas { # Default pagination (offset) should apply
                    edges { node { idVisita } cursor }
                    pageInfo { hasNextPage hasPreviousPage startCursor endCursor }
                    totalCount
                }
            }
        """
        data = self._run_query(query)
        connection = data.get("getVisitas")
        self.assertIsNotNone(connection)
        self.assertIn("edges", connection)
        self.assertIn("pageInfo", connection)
        self.assertIn("totalCount", connection)
        self.assertIsInstance(connection["edges"], list)
        self.assertEqual(connection["totalCount"], self.TOTAL_VISITAS)
        # Check default page size
        self.assertLessEqual(len(connection["edges"]), DEFAULT_PAGE_SIZE)
        if self.TOTAL_VISITAS > DEFAULT_PAGE_SIZE:
             self.assertTrue(connection["pageInfo"]["hasNextPage"])
        else:
             self.assertFalse(connection["pageInfo"]["hasNextPage"])
        self.assertFalse(connection["pageInfo"]["hasPreviousPage"])
        if len(connection["edges"]) > 0:
            self.assertIsNotNone(connection["pageInfo"]["startCursor"])
            self.assertIsNotNone(connection["pageInfo"]["endCursor"])

    def test_get_visitas_filter_by_domain_connection(self):
        """Test filtering visits by domain name with connection structure."""
        query = """
            query GetVisitas($filter: VisitaFilterInput) {
                getVisitas(filter: $filter) {
                    edges { node { idVisita nomeDominio } cursor }
                    pageInfo { startCursor endCursor }
                    totalCount
                }
            }
        """
        domain_to_filter = "example.com"
        variables = { "filter": { "nomeDominio": { "equals": domain_to_filter } } }
        data = self._run_query(query, variables)
        connection = data.get("getVisitas")
        self.assertIsNotNone(connection)
        self.assertGreater(len(connection["edges"]), 0)
        # Cannot easily verify totalCount here without running a separate filtered count
        for edge in connection["edges"]:
            self.assertEqual(edge["node"]["nomeDominio"], domain_to_filter)
            self.assertIsNotNone(edge["cursor"])

    # --- Tests for Etapa 10 Filters (Modified for Connection structure) ---

    def test_filter_timestamp_between_connection(self):
        """Test filtering by timestamp using BETWEEN with connection."""
        query = """
            query GetVisitas($filter: VisitaFilterInput) {
                getVisitas(filter: $filter) {
                    edges { node { idVisita timestampVisita } }
                    totalCount
                }
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
        self.assertTrue(connection["totalCount"] > 0)
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
                getVisitas(filter: $filter) {
                    edges { node { idVisita nomeDominio tipoDispositivo } }
                    totalCount
                }
            }
        """
        variables = {
            "filter": { "AND": [ {"nomeDominio": {"equals": "example.com"}}, {"tipoDispositivo": {"equals": "Desktop"}} ] }
        }
        data = self._run_query(query, variables)
        connection = data.get("getVisitas")
        self.assertIsNotNone(connection)
        self.assertTrue(len(connection["edges"]) > 0)
        self.assertTrue(connection["totalCount"] > 0)
        for edge in connection["edges"]:
            self.assertEqual(edge["node"]["nomeDominio"], "example.com")
            self.assertEqual(edge["node"]["tipoDispositivo"], "Desktop")

    def test_filter_explicit_or_connection(self):
        """Test filtering using explicit OR with connection."""
        query = """
            query GetVisitas($filter: VisitaFilterInput) {
                getVisitas(filter: $filter) {
                     edges { node { idVisita nomeNavegador } }
                     totalCount
                }
            }
        """
        variables = {
            "filter": { "OR": [ {"nomeNavegador": {"equals": "Chrome"}}, {"nomeNavegador": {"equals": "Firefox"}} ] }
        }
        data = self._run_query(query, variables)
        connection = data.get("getVisitas")
        self.assertIsNotNone(connection)
        self.assertTrue(len(connection["edges"]) > 0)
        self.assertTrue(connection["totalCount"] > 0)
        for edge in connection["edges"]:
            self.assertIn(edge["node"]["nomeNavegador"], ["Chrome", "Firefox"])

    # --- Tests for Etapa 11: Cursor Pagination (Add totalCount check) ---

    def test_pagination_first_n(self):
        """Test fetching the first N items."""
        n = 5
        query = """
            query GetFirstN($first: Int) {
                getVisitas(first: $first) {
                    edges { node { idVisita } cursor }
                    pageInfo { hasNextPage hasPreviousPage startCursor endCursor }
                    totalCount
                }
            }
        """
        variables = {"first": n}
        data = self._run_query(query, variables)
        connection = data.get("getVisitas")
        self.assertIsNotNone(connection)
        self.assertEqual(len(connection["edges"]), n)
        self.assertEqual(connection["totalCount"], self.TOTAL_VISITAS)
        self.assertTrue(connection["pageInfo"]["hasNextPage"])
        self.assertFalse(connection["pageInfo"]["hasPreviousPage"])
        self.assertIsNotNone(connection["pageInfo"]["startCursor"])
        self.assertIsNotNone(connection["pageInfo"]["endCursor"])

    def test_pagination_forward_after(self):
        """Test fetching the next page using first and after."""
        n1 = 3
        n2 = 4
        query1 = """ query GetFirst($first: Int) { getVisitas(first: $first) { edges { cursor } pageInfo { endCursor hasNextPage } totalCount } } """
        variables1 = {"first": n1}
        data1 = self._run_query(query1, variables1)
        connection1 = data1.get("getVisitas")
        self.assertTrue(connection1["pageInfo"]["hasNextPage"])
        last_cursor = connection1["pageInfo"]["endCursor"]
        self.assertIsNotNone(last_cursor)
        self.assertEqual(connection1["totalCount"], self.TOTAL_VISITAS)

        query2 = """ query GetNext($first: Int, $after: String) { getVisitas(first: $first, after: $after) { edges { node { idVisita } cursor } pageInfo { hasNextPage hasPreviousPage startCursor endCursor } totalCount } } """
        variables2 = {"first": n2, "after": last_cursor}
        data2 = self._run_query(query2, variables2)
        connection2 = data2.get("getVisitas")
        self.assertIsNotNone(connection2)
        self.assertEqual(len(connection2["edges"]), n2)
        self.assertEqual(connection2["totalCount"], self.TOTAL_VISITAS)
        if self.TOTAL_VISITAS > n1 + n2: self.assertTrue(connection2["pageInfo"]["hasNextPage"])
        self.assertNotEqual(connection1["pageInfo"]["endCursor"], connection2["pageInfo"]["endCursor"])

    def test_pagination_last_n(self):
        """Test fetching the last N items."""
        n = 6
        query = """
            query GetLastN($last: Int) {
                getVisitas(last: $last) {
                    edges { node { idVisita } cursor }
                    pageInfo { hasNextPage hasPreviousPage startCursor endCursor }
                    totalCount
                }
            }
        """
        variables = {"last": n}
        data = self._run_query(query, variables)
        connection = data.get("getVisitas")
        self.assertIsNotNone(connection)
        self.assertEqual(len(connection["edges"]), n)
        self.assertEqual(connection["totalCount"], self.TOTAL_VISITAS)
        self.assertFalse(connection["pageInfo"]["hasNextPage"])
        self.assertTrue(connection["pageInfo"]["hasPreviousPage"])
        self.assertIsNotNone(connection["pageInfo"]["startCursor"])
        self.assertIsNotNone(connection["pageInfo"]["endCursor"])

    def test_pagination_backward_before(self):
        """Test fetching the previous page using last and before."""
        n1 = 7
        n2 = 4
        query1 = """ query GetLast($last: Int) { getVisitas(last: $last) { edges { cursor } pageInfo { startCursor hasPreviousPage } totalCount } } """
        variables1 = {"last": n1}
        data1 = self._run_query(query1, variables1)
        connection1 = data1.get("getVisitas")
        self.assertTrue(connection1["pageInfo"]["hasPreviousPage"])
        first_cursor = connection1["pageInfo"]["startCursor"]
        self.assertIsNotNone(first_cursor)
        self.assertEqual(connection1["totalCount"], self.TOTAL_VISITAS)

        query2 = """ query GetPrevious($last: Int, $before: String) { getVisitas(last: $last, before: $before) { edges { node { idVisita } cursor } pageInfo { hasNextPage hasPreviousPage startCursor endCursor } totalCount } } """
        variables2 = {"last": n2, "before": first_cursor}
        data2 = self._run_query(query2, variables2)
        connection2 = data2.get("getVisitas")
        self.assertIsNotNone(connection2)
        self.assertEqual(len(connection2["edges"]), n2)
        self.assertEqual(connection2["totalCount"], self.TOTAL_VISITAS)
        if self.TOTAL_VISITAS > n1 + n2: self.assertTrue(connection2["pageInfo"]["hasPreviousPage"])
        self.assertNotEqual(connection1["pageInfo"]["startCursor"], connection2["pageInfo"]["startCursor"])

    def test_pagination_with_filter(self):
        """Test pagination combined with filters."""
        n = 2
        query = """
            query GetFilteredPaginated($first: Int, $after: String, $filter: VisitaFilterInput) {
                getVisitas(first: $first, after: $after, filter: $filter) {
                    edges { node { idVisita nomeDominio } cursor }
                    pageInfo { endCursor hasNextPage }
                    totalCount
                }
            }
        """
        variables = { "first": n, "filter": {"nomeDominio": {"equals": "example.com"}} }
        data1 = self._run_query(query, variables)
        connection1 = data1.get("getVisitas")
        self.assertIsNotNone(connection1)
        self.assertLessEqual(len(connection1["edges"]), n)
        self.assertTrue(connection1["totalCount"] > 0) # Expect filtered results
        for edge in connection1["edges"]: self.assertEqual(edge["node"]["nomeDominio"], "example.com")

        if connection1["pageInfo"]["hasNextPage"]:
            variables["after"] = connection1["pageInfo"]["endCursor"]
            data2 = self._run_query(query, variables)
            connection2 = data2.get("getVisitas")
            self.assertIsNotNone(connection2)
            self.assertLessEqual(len(connection2["edges"]), n)
            self.assertEqual(connection2["totalCount"], connection1["totalCount"]) # Total count should be consistent
            for edge in connection2["edges"]: self.assertEqual(edge["node"]["nomeDominio"], "example.com")
            self.assertNotEqual(connection1["pageInfo"]["endCursor"], connection2["pageInfo"]["endCursor"])

    # --- New Tests for Etapa 12: Hybrid Pagination ---

    def test_pagination_offset_limit(self):
        """Test offset/limit pagination."""
        limit = 10
        offset = 5
        query = """
            query GetOffset($limit: Int, $offset: Int) {
                getVisitas(limit: $limit, offset: $offset) {
                    edges { node { idVisita } cursor }
                    pageInfo { hasNextPage hasPreviousPage startCursor endCursor }
                    totalCount
                }
            }
        """
        variables = {"limit": limit, "offset": offset}
        data = self._run_query(query, variables)
        connection = data.get("getVisitas")
        self.assertIsNotNone(connection)
        self.assertEqual(len(connection["edges"]), limit)
        self.assertEqual(connection["totalCount"], self.TOTAL_VISITAS)
        self.assertTrue(connection["pageInfo"]["hasPreviousPage"]) # offset > 0
        self.assertTrue(connection["pageInfo"]["hasNextPage"]) # Assuming offset+limit < total
        self.assertIsNotNone(connection["pageInfo"]["startCursor"]) # Cursors still generated
        self.assertIsNotNone(connection["pageInfo"]["endCursor"])

    def test_pagination_offset_only(self):
        """Test offset pagination with only offset provided (uses default limit)."""
        offset = DEFAULT_PAGE_SIZE
        query = """
            query GetOffsetOnly($offset: Int) {
                getVisitas(offset: $offset) {
                    edges { node { idVisita } }
                    pageInfo { hasNextPage hasPreviousPage }
                    totalCount
                }
            }
        """
        variables = {"offset": offset}
        data = self._run_query(query, variables)
        connection = data.get("getVisitas")
        self.assertIsNotNone(connection)
        self.assertEqual(len(connection["edges"]), DEFAULT_PAGE_SIZE) # Should return default size
        self.assertEqual(connection["totalCount"], self.TOTAL_VISITAS)
        self.assertTrue(connection["pageInfo"]["hasPreviousPage"])
        if self.TOTAL_VISITAS > offset + DEFAULT_PAGE_SIZE:
            self.assertTrue(connection["pageInfo"]["hasNextPage"])

    def test_pagination_limit_only(self):
        """Test offset pagination with only limit provided (uses offset=0)."""
        limit = 8
        query = """
            query GetLimitOnly($limit: Int) {
                getVisitas(limit: $limit) {
                    edges { node { idVisita } }
                    pageInfo { hasNextPage hasPreviousPage }
                    totalCount
                }
            }
        """
        variables = {"limit": limit}
        data = self._run_query(query, variables)
        connection = data.get("getVisitas")
        self.assertIsNotNone(connection)
        self.assertEqual(len(connection["edges"]), limit)
        self.assertEqual(connection["totalCount"], self.TOTAL_VISITAS)
        self.assertFalse(connection["pageInfo"]["hasPreviousPage"]) # offset = 0
        self.assertTrue(connection["pageInfo"]["hasNextPage"]) # Assuming limit < total

    def test_pagination_default(self):
        """Test default pagination (no args -> offset=0, limit=DEFAULT_PAGE_SIZE)."""
        query = """
            query GetDefault {
                getVisitas {
                    edges { node { idVisita } }
                    pageInfo { hasNextPage hasPreviousPage }
                    totalCount
                }
            }
        """
        data = self._run_query(query)
        connection = data.get("getVisitas")
        self.assertIsNotNone(connection)
        self.assertEqual(len(connection["edges"]), DEFAULT_PAGE_SIZE)
        self.assertEqual(connection["totalCount"], self.TOTAL_VISITAS)
        self.assertFalse(connection["pageInfo"]["hasPreviousPage"])
        if self.TOTAL_VISITAS > DEFAULT_PAGE_SIZE:
            self.assertTrue(connection["pageInfo"]["hasNextPage"])

    def test_pagination_conflict_first_limit(self):
        """Test conflicting arguments: first and limit."""
        query = """ query Conflict { getVisitas(first: 5, limit: 10) { totalCount } } """
        self._run_query(query, expect_error=True)

    def test_pagination_conflict_after_offset(self):
        """Test conflicting arguments: after and offset."""
        # Need a valid cursor first
        data = self._run_query(""" query GetCursor { getVisitas(first: 1) { pageInfo { endCursor } } } """)
        cursor = data["getVisitas"]["pageInfo"]["endCursor"]

        query = """ query Conflict($after: String, $offset: Int) { getVisitas(first: 5, after: $after, offset: $offset) { totalCount } } """
        variables = {"after": cursor, "offset": 5}
        self._run_query(query, variables, expect_error=True)

    def test_pagination_conflict_last_limit(self):
        """Test conflicting arguments: last and limit."""
        query = """ query Conflict { getVisitas(last: 3, limit: 5) { totalCount } } """
        self._run_query(query, expect_error=True)

    def test_pagination_conflict_before_offset(self):
        """Test conflicting arguments: before and offset."""
         # Need a valid cursor first
        data = self._run_query(""" query GetCursor { getVisitas(last: 1) { pageInfo { startCursor } } } """)
        cursor = data["getVisitas"]["pageInfo"]["startCursor"]

        query = """ query Conflict($before: String, $offset: Int) { getVisitas(last: 5, before: $before, offset: $offset) { totalCount } } """
        variables = {"before": cursor, "offset": 5}
        self._run_query(query, variables, expect_error=True)


if __name__ == '__main__':
    unittest.main()
