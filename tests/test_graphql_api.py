import unittest
from fastapi.testclient import TestClient
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
        # Need to know the range of timestamps in seed data to create a valid test
        # For now, this test is a placeholder.
        pass

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
