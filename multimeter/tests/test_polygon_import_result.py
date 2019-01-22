""" Проверка результата импорта из Polygon """

from django.test import TestCase
from multimeter.models import Problem
from multimeter.polygon import ImportResult


class TestPolygonImportResult(TestCase):
    """ Проверка результата импорта из Polygon """

    def _test_import_result_wrapper_all_true(self):
        """ Проверка истинности """
        problem = Problem()
        problem.statement = 'statement'
        problem.solutions = 'solutions'
        problem.checker = 'checker'
        result = ImportResult(problem, "")
        self.assertTrue(result.has_statement)
        self.assertTrue(result.has_solution)
        self.assertTrue(result.has_checker)

    def _test_import_result_wrapper_all_false(self):
        """ Проверка ложности """
        problem = Problem()
        result = ImportResult(problem, "")
        self.assertFalse(result.has_statement)
        self.assertFalse(result.has_solution)
        self.assertFalse(result.has_checker)
