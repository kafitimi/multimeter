import os
import tempfile
import shutil
from pathlib import Path
from zipfile import ZipFile, BadZipFile
import xml.etree.ElementTree as ET
from multimeter.models import Problem, Language

EN = 'english'
RU = 'russian'


def process_archive(_path, _lang=EN):
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
    path = os.path.join(_path, 'problem.xml')
    with open(path, 'r', encoding='utf-8') as file:
        root = ET.parse(file).getroot()
    titles = root.find('names').findall('name')
    title = titles[0].attrib['value']
    for t in titles:
        if t.attrib['language'] == _lang:
            title = t.attrib['value']

    conditions_source = ''
    found, path = try_get_conditions_path(root, _lang)
    if found:
        path = os.path.join(_path, path)
        with open(path, 'r', encoding='utf-8') as file:
            conditions_source = file.read()

    solution_source = ''
    found, path = try_get_solutions_path(root, _lang)
    if found:
        path = os.path.join(_path, path)
        with open(path, 'r', encoding='utf-8') as file:
            solution_source = file.read()

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
    tl = 0
    ml = 0
    tl_node = root.find('judging/testset/time-limit')
    if tl_node is not None:
        tl = int(float(tl_node.text) * 0.001)
    ml_node = root.find('judging/testset/memory-limit')
    if ml_node is not None:
        ml = int(ml_node.text) // (1024 * 1024)
    problem = Problem()
    problem.name = title
    problem.input_file = input_file
    problem.output_file = output_file
    problem.time_limit = tl
    problem.memory_limit = ml
    problem.conditions = conditions_source
    problem.solutions = solution_source
    problem.checker = checker_source
    problem.checker_lang = checker_lang
    result = ImportResult(problem, get_tags(_path))
    return result


def try_get_conditions_path(_xmlroot, _lang):
    found = False
    path = None
    for statement in _xmlroot.find('statements').iter('statement'):
        lang = statement.attrib['language']
        _type = statement.attrib['type']
        if lang == _lang and _type == 'application/x-tex':
            path = statement.attrib['path']
            found = True
    return found, path


def try_get_solutions_path(_xmlroot, _lang):
    found = False
    path = None
    for tutorial in _xmlroot.find('tutorials').iter('tutorial'):
        lang = tutorial.attrib['language']
        _type = tutorial.attrib['type']
        if lang == _lang and _type == 'application/x-tex':
            path = tutorial.attrib['path']
            found = True
    return found, path


def try_get_checker_lang(checker_path):
    extension = Path(checker_path).suffix
    return Language.objects.filter(source_ext=extension).first()


def get_tags(problem_root):
    tags = set()
    tags_path = os.path.join(problem_root, 'tags')
    if os.path.isfile(tags_path):
        with open(tags_path, 'r') as file:
            for tag in file:
                tags.add(tag)
    return tags


class ImportResult:
    def __init__(self, problem, tags):
        self.problem = problem
        self.has_statement = bool(problem.conditions)
        self.has_solution = bool(problem.solutions)
        self.has_checker = bool(problem.checker)
        self.language = problem.checker_lang
        self.tags = tags
