import os
import tempfile
import shutil
import zipfile
import xml.etree.ElementTree as ET
import subprocess


def get_contest(_path, _lang):
    tempdir = tempfile.mkdtemp()
    contest_zip = zipfile.ZipFile(_path)
    contest_zip.extractall(tempdir)
    contest_zip.close()
    problems_path = os.path.join(tempdir, "problems")
    for problem_dir in os.listdir(problems_path):
        process_problem(os.path.join(problems_path, problem_dir), _lang)
    shutil.rmtree(tempdir)


def process_problem(_path, _lang):
    source = open(os.path.join(_path, 'problem.xml'), 'rb')
    problem = ET.parse(source)
    root = problem.getroot()
    titles = root.find('names').findall('name');
    title = titles[0].attrib['value']
    for t in titles:
        if t.attrib['language'] == _lang:
            title = t.attrib['value']
    print('Problem found: ' + title)
    statements = root.find('statements')
    statement_path = None
    for s in statements:
        if s.attrib['language'] == _lang and s.attrib['type'] == 'application/x-tex':
            statement_path = s.attrib['path']
    if statement_path:
        print('Statement found: ' + statement_path)
    else:
        print('No statement for {} language'.format(_lang))
    judging = root.find('judging')
    input_file = judging.attrib['input-file']
    output_file = judging.attrib['output-file']
    print('Input file: {}'.format(input_file))
    print('Output file: {}'.format(output_file))
    testsets = judging.findall('testset')
    for t in testsets:
        testset_name = t.attrib['name']
        print('Found testset: {}'.format(testset_name))
        tl = int(float(t.find('time-limit').text) * 0.001)
        ml = int(t.find('memory-limit').text) // (1024 * 1024)
        print('tl: {} sec'.format(tl))
        print('ml: {} mb'.format(ml))
    doall = os.path.join(_path, 'doall.bat')
    print('Building {}...'.format(title), end='')
    if subprocess.call(doall, cwd=_path, shell=True) == 0:
        print(' OK')
    else:
        print(' ERROR')
    print('DONE')
    source.close()


if __name__ == "__main__":
    path = input('path to contest.zip file: ')
    lang = input('lang (leave blank for \'russian\'): ')
    if lang == '':
        lang = 'russian'
    get_contest(path, lang)
