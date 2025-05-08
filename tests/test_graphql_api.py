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
        response = self.client.post("/graphql", json={"query": query})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsNotNone(data.get("data"))
        visitas = data["data"].get("getVisitas")
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
        response = self.client.post("/graphql", json={"query": query, "variables": variables})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsNotNone(data.get("data"))
        visitas = data["data"].get("getVisitas")
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
        response = self.client.post("/graphql", json={"query": query, "variables": variables})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsNotNone(data.get("data"))
        visitas = data["data"].get("getVisitas")
        self.assertIsNotNone(visitas)
        # Assuming seed data includes visits matching this criteria
        # self.assertGreater(len(visitas), 0)
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
        # Timestamps from seed_data.py are all on 2023-01-01
        # The DimTempo entries range from 2023-01-01 00:00:00 to 2023-01-01 16:30:00
        # FatoVisitas.timestamp_visita is a Unix timestamp derived from these.
        # The GraphQL filter expects ISO datetime strings.

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
        response = self.client.post("/graphql", json={"query": query, "variables": variables})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsNotNone(data.get("data"))
        visitas = data["data"].get("getVisitas")
        self.assertIsNotNone(visitas)
        self.assertGreater(len(visitas), 0) # Expect some visits in this range

        # Convert filter times to Unix timestamps for comparison, as VisitaType.timestampVisita resolves to Int (Unix timestamp)
        start_ts_unix = int(start_time_dt.timestamp())
        end_ts_unix = int(end_time_dt.timestamp())

        for visita in visitas:
            self.assertIsNotNone(visita.get("timestampVisita"))
            visita_ts_str = visita["timestampVisita"]
            self.assertIsInstance(visita_ts_str, str)
            # The resolver returns ISO format string. Convert it to a datetime object.
            # The string might or might not have Z for UTC. datetime.fromisoformat handles this.
            # If it includes microseconds, they need to be handled or stripped if not consistent.
            # Assuming the format is like '2023-01-01T08:00:19' or '2023-01-01T08:00:19Z'
            # If it has timezone offset like +00:00, fromisoformat handles it.
            try:
                visita_dt = datetime.datetime.fromisoformat(visita_ts_str.replace('Z', '+00:00'))
            except ValueError:
                 # Handle cases where timezone might not be 'Z' but an offset, or no tz info
                 # For simplicity, if it fails, assume it's naive and UTC (consistent with seed data generation)
                 # This part might need adjustment based on actual resolver output format
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
        response = self.client.post("/graphql", json={"query": query, "variables": variables})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsNotNone(data.get("data"))
        visitas = data["data"].get("getVisitas")
        self.assertIsNotNone(visitas)
        # Assuming seed data includes visits with utm_source containing "goo" (e.g., "google")
        # self.assertGreater(len(visitas), 0)
        for visita in visitas:
            self.assertIsNotNone(visita["utmSource"])
            self.assertIn("goo", visita["utmSource"])


if __name__ == '__main__':
    unittest.main()
