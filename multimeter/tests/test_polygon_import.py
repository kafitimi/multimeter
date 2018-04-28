from django.test import TestCase
from multimeter.models import Account, Problem
import multimeter.polygon as polygon

'''
simple tests
just to check that importer can actually do something
'''


class TestPolygonImport(TestCase):

    def setUp(self):
        self.author = Account()
        self.author.username = 'polygon'
        self.author.set_password('polygon')
        self.author.is_superuser = True
        self.author.save()
        problem = polygon.process_problem('multimeter\\tests\\test_problem', polygon.EN)
        problem.author = self.author
        problem.save()
        checker_source_path = 'multimeter\\tests\\test_problem\\files\\check.cpp'
        with open(checker_source_path) as checker_source_file:
            self.checker_source = checker_source_file.read()

    def test_base_data(self):
        problem = Problem.objects.get(name='Fire stations')
        self.assertEqual(problem.author, self.author)
        self.assertEqual(problem.input_file, 'fire.in')
        self.assertEqual(problem.output_file, 'fire.out')
        self.assertEqual(problem.time_limit, 2)
        self.assertEqual(problem.memory_limit, 64)

    def test_checker_source(self):
        problem = Problem.objects.get(name='Fire stations')
        self.assertEqual(problem.checker, self.checker_source)
