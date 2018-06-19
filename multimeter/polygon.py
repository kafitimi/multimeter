""" Импорт из Polygon """

import os
import tempfile
import shutil
from pathlib import Path
from zipfile import ZipFile, BadZipFile
import xml.etree.ElementTree as ET
from multimeter.models import Problem, Language

EN = 'english'
RU = 'russian'


class ResourceSearchResult:
    """ Результат поиска ресурса """
    def __init__(self, found, path, encoding):
        self.found = found
        self.path = path
        self.encoding = encoding


def process_archive(_path, _lang=EN):
    """ Обработать архив """
    problems = []
    tempdir = tempfile.mkdtemp()
    try:
        contest_zip = ZipFile(_path)
    except BadZipFile:
        return problems
    try:
        contest_zip.extractall(tempdir)
    except IOError:
        return problems
    contest_zip.close()
    if os.path.isfile(os.path.join(tempdir, "contest.xml")):
        problems_path = os.path.join(tempdir, "problems")
        for problem_dir in os.listdir(problems_path):
            problem = process_problem(os.path.join(problems_path, problem_dir), _lang)
            problems.append(problem)
    elif os.path.isfile(os.path.join(tempdir, "problem.xml")):
        problems.append(process_problem(tempdir, _lang))
    shutil.rmtree(tempdir)
    return problems


def process_problem(_path, _lang=EN):
    """ Обработка задачи """
    path = os.path.join(_path, 'problem.xml')
    with open(path, 'r', encoding='utf-8') as file:
        root = ET.parse(file).getroot()
    titles = root.find('names').findall('name')
    title = titles[0].attrib['value']
    for t in titles:
        if t.attrib['language'] == _lang:
            title = t.attrib['value']

    condition = try_get_condition_resource(root, _lang)
    if condition.found:
        path = os.path.join(_path, condition.path)
        with open(path, 'r', encoding=condition.encoding) as file:
            conditions_source = file.read()
    else:
        conditions_source = ''

    solution = try_get_solution_resource(root, _lang)
    if solution.found:
        path = os.path.join(_path, solution.path)
        with open(path, 'r', encoding=solution.encoding) as file:
            solution_source = file.read()
    else:
        solution_source = ''

    checker_source = ''
    checker_lang = None
    source_node = root.find('assets/checker/source')
    if source_node is not None:
        path = os.path.join(_path, source_node.attrib['path'])
        checker_lang = try_get_checker_lang(path)
        with open(path, 'r') as checker_file:
            checker_source = checker_file.read()
    judging = root.find('judging')
    input_file = judging.attrib['input-file']
    output_file = judging.attrib['output-file']
    time_limit = 0
    memory_limit = 0
    tl_node = root.find('judging/testset/time-limit')
    if tl_node is not None:
        time_limit = int(float(tl_node.text) * 0.001)
    ml_node = root.find('judging/testset/memory-limit')
    if ml_node is not None:
        memory_limit = int(ml_node.text) // (1024 * 1024)

    problem = Problem()
    problem.codename = title
    problem.input_file = input_file
    problem.output_file = output_file
    problem.time_limit = time_limit
    problem.memory_limit = memory_limit
    # problem.conditions = conditions_source
    # problem.solutions = solution_source
    problem.checker = checker_source
    problem.checker_lang = checker_lang

    result = ImportResult(problem, get_tags(root))
    return result


def try_get_condition_resource(_xmlroot, _lang) -> ResourceSearchResult:
    """ Получить условия """
    return try_get_resource(_xmlroot, 'statements', 'statement', _lang)


def try_get_solution_resource(_xmlroot, _lang) -> ResourceSearchResult:
    """ Получить решение """
    return try_get_resource(_xmlroot, 'tutorials', 'tutorial', _lang)


def try_get_resource(_xmlroot, parent_node: str, child_node: str, _lang: str):
    """ Получить ресурс (решение / условия) """
    for tutorial in _xmlroot.find(parent_node).iter(child_node):
        lang = tutorial.attrib['language']
        _type = tutorial.attrib['type']
        if lang == _lang and _type == 'application/x-tex':
            found = True
            path = tutorial.attrib['path']
            encoding = tutorial.attrib['charset']
            break
    return ResourceSearchResult(found, path, encoding)


def try_get_checker_lang(checker_path):
    """ Получить язык программирования на котором написан чекер """
    extension = Path(checker_path).suffix
    return Language.objects.filter(source_ext=extension).first()


def get_tags(_xmlroot):
    """ Получить теги """
    tags = set()
    root = _xmlroot.find('tags')
    if root is None:
        return tags
    for tag in root.iter('tag'):
        tags.add(tag.attrib['value'])
    return tags


class ImportResult:
    """ Результат импорта """
    def __init__(self, problem, tags):
        self.problem = problem
        # self.has_statement = bool(problem.conditions)
        # self.has_solution = bool(problem.solutions)
        self.has_checker = bool(problem.checker)
        self.language = problem.checker_lang
        self.tags = tags
