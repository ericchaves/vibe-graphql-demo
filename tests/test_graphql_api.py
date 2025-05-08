import unittest
from fastapi.testclient import TestClient # type: ignore
import sqlite3
import os
import datetime
import time

# Assuming main.py and init_db.py are in the parent directory
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import app
from init_db import init_db, DATABASE_FILE
from seed_data import seed_data

class TestGraphQLAPI(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Set up the test database and seed data once for all tests."""
        # Ensure a clean database for testing
        if os.path.exists(DATABASE_FILE):
            os.remove(DATABASE_FILE)
        init_db()
        seed_data()
        cls.client = TestClient(app)

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
        response = self.client.post("/graphql", json=json_payload)
        self.assertEqual(response.status_code, 200, f"GraphQL query failed: {response.text}")
        data = response.json()
        self.assertIsNone(data.get("errors"), f"GraphQL errors: {data.get('errors')}")
        self.assertIsNotNone(data.get("data"), "GraphQL response missing data.")
        return data["data"]

    def test_get_visitas_no_filter(self):
        """Test fetching all visits without any filter."""
        query = """
            query {
                getVisitas {
                    idVisita
                    nomeDominio
                    caminhoPagina
                    urlCompleta
                    nomeNavegador
                    soUsuarioNavegador
                    tipoDispositivo
                    enderecoIp
                    paisGeografia
                    tipoReferencia
                }
            }
        """
        data = self._run_query(query)
        visitas = data.get("getVisitas")
        self.assertIsNotNone(visitas)
        self.assertGreater(len(visitas), 0) # Assuming seed_data adds some visits

    def test_get_visitas_filter_by_domain(self):
        """Test filtering visits by domain name."""
        query = """
            query GetVisitas($filter: VisitaFilterInput) {
                getVisitas(filter: $filter) {
                    idVisita
                    nomeDominio
                }
            }
        """
        variables = {
            "filter": {
                "nomeDominio": {
                    "equals": "example.com"
                }
            }
        }
        data = self._run_query(query, variables)
        visitas = data.get("getVisitas")
        self.assertIsNotNone(visitas)
        self.assertGreater(len(visitas), 0)
        for visita in visitas:
            self.assertEqual(visita["nomeDominio"], "example.com")

    def test_get_visitas_filter_by_device_type_and_browser(self):
        """Test filtering visits by device type and browser name."""
        query = """
            query GetVisitas($filter: VisitaFilterInput) {
                getVisitas(filter: $filter) {
                    idVisita
                    tipoDispositivo
                    nomeNavegador
                }
            }
        """
        variables = {
            "filter": {
                "tipoDispositivo": {
                    "equals": "Mobile"
                },
                "nomeNavegador": {
                    "equals": "Safari"
                }
            }
        }
        data = self._run_query(query, variables)
        visitas = data.get("getVisitas")
        self.assertIsNotNone(visitas)
        # Assuming seed data includes visits matching this criteria
        # self.assertGreater(len(visitas), 0) # Check if seed data guarantees this
        for visita in visitas:
            self.assertEqual(visita["tipoDispositivo"], "Mobile")
            self.assertEqual(visita["nomeNavegador"], "Safari")

    def test_get_visitas_filter_by_timestamp_range(self):
        """Test filtering visits by timestamp within a range."""
        query = """
            query GetVisitas($filter: VisitaFilterInput) {
                getVisitas(filter: $filter) {
                    idVisita
                    timestampVisita # Ensure this field is in VisitaType and returns ISO string or Unix timestamp
                }
            }
        """
        start_time_dt = datetime.datetime(2023, 1, 1, 8, 0, 0, tzinfo=datetime.timezone.utc)
        end_time_dt = datetime.datetime(2023, 1, 1, 12, 0, 0, tzinfo=datetime.timezone.utc)

        variables = {
            "filter": {
                "timestampVisita": {
                    "greaterThanOrEqual": start_time_dt.isoformat(),
                    "lessThanOrEqual": end_time_dt.isoformat()
                }
            }
        }
        data = self._run_query(query, variables)
        visitas = data.get("getVisitas")
        self.assertIsNotNone(visitas)
        self.assertGreater(len(visitas), 0) # Expect some visits in this range

        start_ts_unix = int(start_time_dt.timestamp())
        end_ts_unix = int(end_time_dt.timestamp())

        for visita in visitas:
            self.assertIsNotNone(visita.get("timestampVisita"))
            visita_ts_str = visita["timestampVisita"]
            self.assertIsInstance(visita_ts_str, str)
            try:
                visita_dt = datetime.datetime.fromisoformat(visita_ts_str.replace('Z', '+00:00'))
            except ValueError:
                visita_dt = datetime.datetime.fromisoformat(visita_ts_str)
                if visita_dt.tzinfo is None:
                    visita_dt = visita_dt.replace(tzinfo=datetime.timezone.utc)

            visita_ts_unix = int(visita_dt.timestamp())
            self.assertGreaterEqual(visita_ts_unix, start_ts_unix)
            self.assertLessEqual(visita_ts_unix, end_ts_unix)

    def test_get_visitas_filter_by_utm_source_contains(self):
        """Test filtering visits by UTM source using contains."""
        query = """
            query GetVisitas($filter: VisitaFilterInput) {
                getVisitas(filter: $filter) {
                    idVisita
                    utmSource
                }
            }
        """
        variables = {
            "filter": {
                "utmSource": {
                    "contains": "goo"
                }
            }
        }
        data = self._run_query(query, variables)
        visitas = data.get("getVisitas")
        self.assertIsNotNone(visitas)
        # Assuming seed data includes visits with utm_source containing "goo" (e.g., "google")
        # self.assertGreater(len(visitas), 0) # Check if seed data guarantees this
        for visita in visitas:
            self.assertIsNotNone(visita["utmSource"])
            self.assertIn("goo", visita["utmSource"])

    # --- New Tests for Etapa 10 ---

    def test_filter_timestamp_between(self):
        """Test filtering by timestamp using BETWEEN."""
        query = """
            query GetVisitas($filter: VisitaFilterInput) {
                getVisitas(filter: $filter) { idVisita timestampVisita }
            }
        """
        start_time = datetime.datetime(2023, 1, 1, 9, 0, 0, tzinfo=datetime.timezone.utc)
        end_time = datetime.datetime(2023, 1, 1, 11, 0, 0, tzinfo=datetime.timezone.utc)
        variables = {
            "filter": {
                "timestampVisita": {
                    "between": [start_time.isoformat(), end_time.isoformat()]
                }
            }
        }
        data = self._run_query(query, variables)
        visitas = data.get("getVisitas")
        self.assertIsNotNone(visitas)
        self.assertTrue(len(visitas) > 0) # Expect results
        start_ts = start_time.timestamp()
        end_ts = end_time.timestamp()
        for v in visitas:
            visita_dt = datetime.datetime.fromisoformat(v["timestampVisita"].replace('Z', '+00:00'))
            visita_ts = visita_dt.timestamp()
            self.assertTrue(start_ts <= visita_ts <= end_ts)

    def test_filter_ano_not_between(self):
        """Test filtering by year using NOT BETWEEN."""
        query = """
            query GetVisitas($filter: VisitaFilterInput) {
                getVisitas(filter: $filter) { idVisita ano }
            }
        """
        # Seed data only has 2023
        variables = {
            "filter": { "ano": { "notBetween": [2020, 2022] } }
        }
        data = self._run_query(query, variables)
        visitas = data.get("getVisitas")
        self.assertIsNotNone(visitas)
        self.assertTrue(len(visitas) > 0)
        for v in visitas:
            self.assertEqual(v["ano"], 2023)

    def test_filter_explicit_and(self):
        """Test filtering using explicit AND."""
        query = """
            query GetVisitas($filter: VisitaFilterInput) {
                getVisitas(filter: $filter) { idVisita nomeDominio tipoDispositivo }
            }
        """
        variables = {
            "filter": {
                "AND": [
                    {"nomeDominio": {"equals": "example.com"}},
                    {"tipoDispositivo": {"equals": "Desktop"}}
                ]
            }
        }
        data = self._run_query(query, variables)
        visitas = data.get("getVisitas")
        self.assertIsNotNone(visitas)
        self.assertTrue(len(visitas) > 0) # Assuming seed data has this combo
        for v in visitas:
            self.assertEqual(v["nomeDominio"], "example.com")
            self.assertEqual(v["tipoDispositivo"], "Desktop")

    def test_filter_explicit_or(self):
        """Test filtering using explicit OR."""
        query = """
            query GetVisitas($filter: VisitaFilterInput) {
                getVisitas(filter: $filter) { idVisita nomeNavegador }
            }
        """
        variables = {
            "filter": {
                "OR": [
                    {"nomeNavegador": {"equals": "Chrome"}},
                    {"nomeNavegador": {"equals": "Firefox"}}
                ]
            }
        }
        data = self._run_query(query, variables)
        visitas = data.get("getVisitas")
        self.assertIsNotNone(visitas)
        self.assertTrue(len(visitas) > 0) # Assuming seed data has these browsers
        for v in visitas:
            self.assertIn(v["nomeNavegador"], ["Chrome", "Firefox"])

    def test_filter_nested_and_or(self):
        """Test filtering with nested AND/OR logic."""
        query = """
            query GetVisitas($filter: VisitaFilterInput) {
                getVisitas(filter: $filter) { idVisita nomeDominio paisGeografia nomeNavegador }
            }
        """
        # Find visits from example.com that are either from USA OR using Chrome browser
        variables = {
            "filter": {
                "AND": [
                    {"nomeDominio": {"equals": "example.com"}},
                    {
                        "OR": [
                            {"paisGeografia": {"equals": "USA"}},
                            {"nomeNavegador": {"equals": "Chrome"}}
                        ]
                    }
                ]
            }
        }
        data = self._run_query(query, variables)
        visitas = data.get("getVisitas")
        self.assertIsNotNone(visitas)
        self.assertTrue(len(visitas) > 0) # Assuming seed data allows this
        for v in visitas:
            self.assertEqual(v["nomeDominio"], "example.com")
            self.assertTrue(v["paisGeografia"] == "USA" or v["nomeNavegador"] == "Chrome")

    def test_filter_direct_and_or_combination(self):
        """Test combination of direct field filters and OR block."""
        query = """
            query GetVisitas($filter: VisitaFilterInput) {
                getVisitas(filter: $filter) { idVisita nomeDominio tipoDispositivo nomeNavegador }
            }
        """
        # Find visits from example.com that are either Desktop OR Chrome
        # Top-level fields are ANDed with the OR block
        variables = {
            "filter": {
                "nomeDominio": {"equals": "example.com"},
                "OR": [
                    {"tipoDispositivo": {"equals": "Desktop"}},
                    {"nomeNavegador": {"equals": "Chrome"}}
                ]
            }
        }
        data = self._run_query(query, variables)
        visitas = data.get("getVisitas")
        self.assertIsNotNone(visitas)
        self.assertTrue(len(visitas) > 0)
        for v in visitas:
            self.assertEqual(v["nomeDominio"], "example.com")
            self.assertTrue(v["tipoDispositivo"] == "Desktop" or v["nomeNavegador"] == "Chrome")


if __name__ == '__main__':
    unittest.main()
