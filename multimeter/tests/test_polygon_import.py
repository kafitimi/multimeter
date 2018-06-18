'''
simple tests
just to check that importer can actually do something
'''

from django.test import TestCase
from multimeter.models import Account, Problem
import multimeter.polygon as polygon


class TestPolygonImport(TestCase):
    """ Тестирование импорта из Polygon """

    def setUp(self):
        self.author = Account()
        self.author.username = 'polygon'
        self.author.set_password('polygon')
        self.author.is_superuser = True
        self.author.save()

        problem = polygon.process_problem('multimeter\\tests\\test_problem', polygon.EN).problem
        problem.author = self.author
        problem.save()

        checker_source_path = 'multimeter\\tests\\test_problem\\files\\check.cpp'
        with open(checker_source_path) as checker_source_file:
            self.checker_source = checker_source_file.read()
        statement_source_path = 'multimeter\\tests\\test_problem\\statements\\english\\problem.tex'
        with open(statement_source_path) as file:
            self.statement_source = file.read()
        tutorial_source_path = 'multimeter\\tests\\test_problem\\statements\\english\\tutorial.tex'
        with open(tutorial_source_path) as file:
            self.tutorial_source = file.read()

    def test_base_data(self):
        """ Тестирование да """
        problem = Problem.objects.get(name='Fire stations')
        self.assertEqual(problem.author, self.author)
        self.assertEqual(problem.input_file, 'fire.in')
        self.assertEqual(problem.output_file, 'fire.out')
        self.assertEqual(problem.time_limit, 2)
        self.assertEqual(problem.memory_limit, 64)

    def test_checker_source(self):
        """ Проверить исходный код чекера """
        problem = Problem.objects.get(name='Fire stations')
        self.assertEqual(problem.checker, self.checker_source)

    def test_statement_source(self):
        """ Проверить исходный код условия """
        problem = Problem.objects.get(name='Fire stations')
        self.assertEqual(problem.conditions, self.statement_source)

    def test_solution_source(self):
        """ Проверить исходный код решения """
        problem = Problem.objects.get(name='Fire stations')
        self.assertEqual(problem.solutions, self.tutorial_source)
