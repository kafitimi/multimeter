""" Multimeter models """

from django.db.models import (Model, BooleanField, CASCADE, CharField, IntegerField, ForeignKey,
                              TextField, DateTimeField, DateField, ManyToManyField)
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _


CE = 'CE'
RE = 'RE'
ML = 'ML'
TL = 'TL'
WA = 'WA'
OK = 'OK'

COMPILATION_RESULTS = (
    (CE, 'Compilation error'),
    (OK, 'OK'),
)

EXECUTION_RESULTS = (
    (RE, 'Runtime error'),
    (ML, 'Memory limit'),
    (TL, 'Time limit'),
    (WA, 'Wrong answer'),
    (OK, 'OK'),
)

DEFAULT_PROBLEM_TEXT_LANGUAGE = 'english'

PROBLEM_TEXT_LANGUAGES = (
    DEFAULT_PROBLEM_TEXT_LANGUAGE,
    'russian',
)


class CountryReference(Model):
    """
    Справочник государств
    """
    name = CharField(_('name'), max_length=50)

    class Meta:
        verbose_name = _('country')
        verbose_name_plural = _('countries')

    def __str__(self):
        return self.name


class Account(AbstractUser):
    """
    Учетная запись пользователя
    Флаг is_staff означает автора задачи.
    Флаг is_admin означает организатора контеста.
    Дополнительные атрибуты нужны для заполнения протоколов.
    """
    second_name = CharField(_('second name'), max_length=50, blank=True, default='')
    birthday = DateField(_('birthday'), blank=True, null=True)
    country = ForeignKey('CountryReference', on_delete=CASCADE, blank=True, null=True,
                         verbose_name=_('country'))
    participations = ManyToManyField('Contest', verbose_name=_('participations'), blank=True)

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def __str__(self):
        answer = self.username
        if self.last_name or self.first_name:
            name = '%s %s' % (self.last_name, self.first_name)
            answer = '%s (%s)' % (name.strip(), answer)
        return answer


class Contest(Model):
    """
    Контест
    Краткое наименование нужно для внутреннего использования. Пример:
    9 класс

    Полное наименование нужно для заголовков. Пример:
    Всероссийская олимпиада школьников по информатике. Региональный этап.

    Флаг personal_rules включает правила личного зачета
    Флаг command_rules включает правила командного зачёта
    Флаги personal_rules и command_rules можно включать одновременно для проведения лично-командной
    олимпиады

    Если флаг active снят, то доступ к олимпиаде разрешен только для организаторов (пользователей с
    флагом staff)

    Флаг anonymous_access разрешает гостевой доступ к условиям задач и опубликованным результатам.

    Участники могут читать условия после времени начала.

    Участники могут отправлять решения между временем начала и временем окончания.

    Если время заморозки задано между временем начала и временем окончания, тогда участники и
    анонимные пользователи могут видеть таблицу результатов во время олимпиады.

    Если задано время публикации результатов участники и гости смогут видеть результаты после этого
    времени.

    Флаг show_tests разрешает участникам и гостям видеть тесты после окончания олимпиады.

    """
    brief_name = CharField(_('brief name'), max_length=100)
    full_name = TextField(_('full name'), blank=True)

    statements = CharField(_('statements filename'), max_length=255, blank=True)
    rules = CharField(_('rules filename'), max_length=255, blank=True)

    start = DateTimeField(_('start time'))
    stop = DateTimeField(_('stop time'))
    freeze = DateTimeField(_('freeze time'), blank=True, null=True)

    personal_rules = BooleanField(_('individual contest rules'), default=False)
    command_rules = BooleanField(_('team contest rules'), default=False)

    guest_access = BooleanField(_('guest access'), default=False)
    participant_access = BooleanField(_('participant access'), default=False)
    show_tests = BooleanField(_('show tests'), default=False)
    show_results = BooleanField(_('show results'), default=False)

    problems = ManyToManyField('multimeter.Problem', through='multimeter.ContestProblem', blank=True)

    class Meta:
        verbose_name = _('contest')
        verbose_name_plural = _('contests')
        ordering = ['brief_name']

    def __str__(self):
        return self.brief_name


class Problem(Model):
    """
    Задача
    """
    codename = CharField(_('codename'), max_length=100)
    input_file = CharField(_('input filename'), max_length=100, blank=True, default='',
                           help_text=_('Standard input will be used if left blank'))
    output_file = CharField(_('output filename'), max_length=100, blank=True, default='',
                            help_text=_('Standard output will be used if left blank'))
    author = ForeignKey('multimeter.Account', on_delete=CASCADE, verbose_name=_('contests'))
    time_limit = IntegerField(_('time limit (ms)'), default=1000)
    memory_limit = IntegerField(_('memory limit (MiB)'), default=64)
    last_modified = DateTimeField(auto_now=True)

    checker = TextField(_('checker'), blank=True)
    checker_lang = ForeignKey('multimeter.Language', on_delete=CASCADE, blank=True, null=True,
                              verbose_name=_('programming language'))

    class Meta:
        verbose_name = _('problem')
        verbose_name_plural = _('problems')
        ordering = ['author', 'codename']

    def __str__(self):
        return "%s (%s)" % (self.codename, self.author)

    def set_tags_from_string(self, new_tags: str):
        """ Сохранение измененного списка тегов """
        new_tags_set = set(new_tags.lower().replace(',', ' ').split())
        self.set_tags(new_tags_set)

    def set_tags(self, tags: set):
        """ Изменение тегов """
        old_tags = {t.tag for t in self.tags.all()}

        tags_to_add = tags - old_tags
        for tag in tags_to_add:
            tag_object, _ = Tag.objects.get_or_create(tag=tag)
            tag_object.problems.add(self)

        tags_to_del = old_tags - tags
        for tag in tags_to_del:
            tag_object, _ = Tag.objects.get_or_create(tag=tag)
            tag_object.problems.remove(self)
            if tag_object.problems.count() == 0:
                tag_object.delete()

    def get_statement_languages(self):
        return {statement.language for statement in self.problemtext_set.all()}

    def get_statements(self, lang):
        return self.problemtext_set.filter(language=lang)

    def set_statements(self, lang, statements):
        for text_type, text in statements:
            if text:
                try:
                    statement = self.problemtext_set.get(text_type=text_type, language=lang)
                    statement.text = text
                    statement.save()
                except ProblemText.DoesNotExist:
                    ProblemText(problem=self, text_type=text_type, text=text, language=lang).save()
            else:
                self.problemtext_set.filter(text_type=text_type, language=lang).delete()



class ProblemText(Model):
    """
    Тексты задачи
    """
    NAME = 1
    LEGEND = 2
    SCORING = 3
    INPUT_FORMAT = 4
    OUTPUT_FORMAT = 5
    TUTORIAL = 6

    TEXT_TYPES = (
        (NAME, _('name')),  # официальное название
        (LEGEND, _('statement')),  # текст условий
        (SCORING, _('scoring')),  # правила начисления баллов
        (INPUT_FORMAT, _('input format')),  # формат входных данных
        (OUTPUT_FORMAT, _('output format')),  # формат выходных данных
        (TUTORIAL, _('tutorial')),  # разбор
    )

    problem = ForeignKey('Problem', on_delete=CASCADE, verbose_name=_('problem'))
    language = CharField(_('language'), max_length=2)
    text_type = IntegerField(_('text type'), choices=TEXT_TYPES)
    text = TextField(_('text'))


class ContestProblem(Model):
    """
    Код задачи в контесте
    """
    code = CharField('код', max_length=10, blank=True)
    contest = ForeignKey('multimeter.Contest', on_delete=CASCADE, verbose_name='олимпиада')
    problem = ForeignKey('multimeter.Problem', on_delete=CASCADE, verbose_name='задача')

    class Meta:
        verbose_name = 'код задачи в олимпиаде'
        verbose_name_plural = 'коды задач в олимпиаде'
        ordering = ['contest', 'code']

    def __str__(self):
        return '%s, задача %s "%s"' % (
            self.contest,
            self.code,
            self.problem,
        )


class SubTask(Model):
    """
    Подзадача
    """
    PARTIAL = 'PRT'
    ENTIRE = 'ENT'

    SCORING = (
        (PARTIAL, _('for each test independently')),
        (ENTIRE, _('only for entire subtask')),
    )

    BRIEF = 'BRF'
    ERROR = 'ERR'
    FULL = 'FUL'

    RESULTS = (
        (BRIEF, _('only for entire subtask')),
        (ERROR, _('up to the first failing test')),
        (FULL, _('for each test independently')),
    )

    problem = ForeignKey('multimeter.Problem', verbose_name='задача', on_delete=CASCADE)
    number = IntegerField('номер по порядку')
    scoring = CharField('начисление баллов', max_length=3, choices=SCORING)
    results = CharField('отображение результатов', max_length=3, choices=RESULTS)

    class Meta:
        verbose_name = 'подзадача'
        verbose_name_plural = 'подзадачи'
        ordering = ['problem', 'number']

    def __str__(self):
        return 'задача "%s", подзадача %s' % (
            self.problem,
            self.number,
        )


class AbstractTest(Model):
    """
    Общий родительский класс для теста и примера
    """
    number = IntegerField('номер по порядку')
    input = TextField('входные данные')
    output = TextField('выходные данные')

    class Meta:
        abstract = True


class Sample(AbstractTest):
    """
    Пример к задаче
    """
    problem = ForeignKey('multimeter.Problem', on_delete=CASCADE, verbose_name='задача')
    required = BooleanField('обязателен при проверке', default=False)

    class Meta:
        verbose_name = 'пример'
        verbose_name_plural = 'примеры'
        ordering = ['problem', 'number']

    def __str__(self):
        return 'задача "%s", пример %s' % (
            self.problem,
            self.number,
        )


class Test(AbstractTest):
    """
    Тест в подзадаче
    """
    sub_task = ForeignKey('multimeter.SubTask', on_delete=CASCADE, verbose_name='подзадача')

    class Meta:
        verbose_name = 'тест'
        verbose_name_plural = 'тесты'
        ordering = ['sub_task', 'number']

    def __str__(self):
        return '%s, тест %s' % (
            self.sub_task,
            self.number,
        )


class Submission(Model):
    """
    Отправка попытки решения на проверку
    """
    contest_problem = ForeignKey('multimeter.ContestProblem', on_delete=CASCADE,
                                 verbose_name='задача')
    user = ForeignKey('multimeter.Account', on_delete=CASCADE)
    language = ForeignKey('multimeter.Language', on_delete=CASCADE,
                          verbose_name='язык программирования')
    number = IntegerField('номер попытки')
    moment = DateTimeField('дата и время отправки', auto_now=True)
    source = TextField('текст решения')

    class Meta:
        verbose_name = 'подзадача'
        verbose_name_plural = 'подзадачи'
        ordering = ['number']

    def set_number(self):
        self.number = Submission.objects.filter(contest_problem=self.contest_problem, user=self.user).count() + 1

    def __str__(self):
        return '%s, пользователь %s, попытка %s' % (
            self.contest_problem,
            self.user,
            self.number,
        )


class Language(Model):
    """
    Язык программирования
    """
    name = CharField('название', max_length=100)
    source_ext = CharField('расширение файла', max_length=5, default='')
    compilation = TextField('строки компиляции')
    execution = TextField('строка выполнения')

    class Meta:
        verbose_name = 'язык программирования'
        verbose_name_plural = 'языки программирования'
        ordering = ['name']

    def __str__(self):
        return self.name


class Check(Model):
    """
    Проверка решения

    Алгоритм работы автоматизированной системы проверки:
    * Веб-сервер получает от участника решение
    * Веб-сервер создает Submission
    * Веб-сервер помещает решение в очередь арбитра
    * Арбитр вынимает решение из очереди
    * Арбитр проверяет решение
    * Арбитр записывает результат в очередь веб-сервера
    * По запросу от браузера веб-сервер проверяет очередь результатов
    * Веб-сервер создает Check, ExampleResult и TestResult
    * Веб-сервер возвращает отчет о проверке участнику
    """
    submission = ForeignKey('multimeter.Submission', on_delete=CASCADE, verbose_name='попытка')
    moment = DateTimeField('дата и время проверки')
    compilation_result = CharField('результат компиляции', max_length=2,
                                   choices=COMPILATION_RESULTS)
    score = IntegerField('баллы')

    class Meta:
        verbose_name = 'проверка решения'
        verbose_name_plural = 'проверки решений'


class TestResult(Model):
    """
    Результат проверки на тесте
    """
    check = ForeignKey('multimeter.Check', on_delete=CASCADE, verbose_name='проверка')
    test = ForeignKey('multimeter.AbstractTest', on_delete=CASCADE, verbose_name='тест')
    execution_result = CharField('результат выполнения', max_length=2, choices=EXECUTION_RESULTS)
    execution_output = TextField('вывод решения')
    execution_code = IntegerField('код возврата решения')
    check_output = IntegerField('вывод чекера')
    check_code = IntegerField('код возврата чекера')
    memory = IntegerField('память (кб)')
    time = IntegerField('время (кб)')

    class Meta:
        abstract = True
        verbose_name = 'результат проверки на тесте'
        verbose_name_plural = 'результаты проверок на тестах'


class Tag(Model):
    """ Теги """
    tag = CharField(max_length=25, unique=True)
    problems = ManyToManyField('Problem', related_name="tags", blank=True)

    class Meta:
        verbose_name = _('tag')
        verbose_name_plural = _('tags')

    def __str__(self):
        return self.tag
