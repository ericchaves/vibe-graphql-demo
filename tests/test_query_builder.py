import unittest
import datetime
from typing import Any

# Assuming schema.py is in the parent directory
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from schema import build_where_clause, VisitaFilterInput, StringFilterInput, IntFilterInput, DateTimeFilterInput

class TestQueryBuilder(unittest.TestCase):

    def test_empty_filter(self):
        filter_input = VisitaFilterInput()
        where_clause, params = build_where_clause(filter_input)
        self.assertEqual(where_clause, "")
        self.assertEqual(params, [])

    def test_string_equals_filter(self):
        filter_input = VisitaFilterInput(nome_dominio=StringFilterInput(equals="example.com"))
        where_clause, params = build_where_clause(filter_input)
        self.assertEqual(where_clause, " WHERE DimDominio.nome_dominio = ?")
        self.assertEqual(params, ["example.com"])

    def test_string_contains_filter(self):
        filter_input = VisitaFilterInput(caminho_pagina=StringFilterInput(contains="product"))
        where_clause, params = build_where_clause(filter_input)
        self.assertEqual(where_clause, " WHERE DimPagina.caminho_pagina LIKE ?")
        self.assertEqual(params, ["%product%"])

    def test_int_greater_than_filter(self):
        filter_input = VisitaFilterInput(ano=IntFilterInput(greaterThan=2022))
        where_clause, params = build_where_clause(filter_input)
        self.assertEqual(where_clause, " WHERE DimTempo.ano > ?")
        self.assertEqual(params, [2022])

    def test_datetime_less_than_filter(self):
        test_time = datetime.datetime(2023, 1, 15, 10, 0, 0)
        filter_input = VisitaFilterInput(timestamp_visita=DateTimeFilterInput(lessThan=test_time))
        where_clause, params = build_where_clause(filter_input)
        self.assertEqual(where_clause, " WHERE FatoVisitas.timestamp_visita < ?")
        self.assertEqual(params, [int(test_time.timestamp())])

    def test_multiple_filters_and(self):
        filter_input = VisitaFilterInput(
            nome_dominio=StringFilterInput(equals="example.com"),
            tipo_dispositivo=StringFilterInput(equals="Mobile")
        )
        where_clause, params = build_where_clause(filter_input)
        # Order of conditions might vary based on dictionary iteration, so check for both possibilities
        expected_clause_1 = " WHERE DimDominio.nome_dominio = ? AND DimDispositivo.tipo_dispositivo = ?"
        expected_clause_2 = " WHERE DimDispositivo.tipo_dispositivo = ? AND DimDominio.nome_dominio = ?"
        self.assertIn(where_clause, [expected_clause_1, expected_clause_2])

        expected_params_1 = ["example.com", "Mobile"]
        expected_params_2 = ["Mobile", "example.com"]
        self.assertIn(params, [expected_params_1, expected_params_2])


    def test_string_in_filter(self):
        filter_input = VisitaFilterInput(nome_navegador=StringFilterInput(In=["Chrome", "Firefox"]))
        where_clause, params = build_where_clause(filter_input)
        self.assertEqual(where_clause, " WHERE DimNavegador.nome_navegador IN (?, ?)")
        self.assertEqual(params, ["Chrome", "Firefox"])

    def test_int_not_in_filter(self):
        filter_input = VisitaFilterInput(mes=IntFilterInput(notIn=[10, 11, 12]))
        where_clause, params = build_where_clause(filter_input)
        self.assertEqual(where_clause, " WHERE DimTempo.mes NOT IN (?, ?, ?)")
        self.assertEqual(params, [10, 11, 12])

    def test_combined_filters(self):
        test_time = datetime.datetime(2023, 5, 1, 0, 0, 0)
        filter_input = VisitaFilterInput(
            pais_geografia=StringFilterInput(equals="USA"),
            timestamp_visita=DateTimeFilterInput(greaterThanOrEqual=test_time),
            tipo_dispositivo=StringFilterInput(notEquals="Tablet")
        )
        where_clause, params = build_where_clause(filter_input)

        # Check for the presence of key parts of the WHERE clause and parameters
        self.assertIn(" WHERE ", where_clause)
        self.assertIn("DimGeografia.pais = ?", where_clause)
        self.assertIn("FatoVisitas.timestamp_visita >= ?", where_clause)
        self.assertIn("DimDispositivo.tipo_dispositivo != ?", where_clause)

        self.assertIn("USA", params)
        self.assertIn(int(test_time.timestamp()), params)
        self.assertIn("Tablet", params)


if __name__ == '__main__':
    unittest.main()
