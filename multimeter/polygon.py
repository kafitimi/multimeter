import os
import tempfile
import shutil
import zipfile
import xml.etree.cElementTree as ET
from multimeter.models import Problem

EN = 'english'
RU = 'russian'


def process_archive(_path, _lang=EN):
    tempdir = tempfile.mkdtemp()
    contest_zip = zipfile.ZipFile(_path)
    contest_zip.extractall(tempdir)
    contest_zip.close()
    problems = []
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
    root = ET.ElementTree(file=path).getroot()
    titles = root.find('names').findall('name')
    title = titles[0].attrib['value']
    for t in titles:
        if t.attrib['language'] == _lang:
            title = t.attrib['value']
    checker_source = ''
    assets_node = root.find('assets')
    if assets_node is not None:
        checker_node = assets_node.find('checker')
        if checker_node is not None:
            source_node = checker_node.find('source')
            if source_node is not None:
                checker_path = os.path.join(_path, source_node.attrib['path'])
                with open(checker_path, 'r') as checker_file:
                    checker_source = checker_file.read()
    judging = root.find('judging')
    input_file = judging.attrib['input-file']
    output_file = judging.attrib['output-file']
    testsets = judging.findall('testset')
    tl = 0
    ml = 0
    for t in testsets:
        tl = int(float(t.find('time-limit').text) * 0.001)
        ml = int(t.find('memory-limit').text) // (1024 * 1024)
    problem = Problem()
    problem.name = title
    problem.input_file = input_file
    problem.output_file = output_file
    problem.time_limit = tl
    problem.memory_limit = ml
    problem.checker = checker_source
    return problem
