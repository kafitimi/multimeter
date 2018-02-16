from django.contrib.contenttypes.models import ContentType
from django.db.models import Model, BooleanField, CASCADE, CharField, IntegerField, ForeignKey, TextField, \
    DateTimeField, DateField
from django.contrib.auth.models import AbstractUser


CE = 'CE'
RE = 'RE'
ML = 'ML'
TL = 'TL'
WA = 'WA'
OK = 'OK'

COMPILATION_RESULTS = [
    (CE, 'Compilation error'),
    (OK, 'OK'),
]

EXECUTION_RESULTS = [
    (RE, 'Runtime error'),
    (ML, 'Memory limit'),
    (TL, 'Time limit'),
    (WA, 'Wrong answer'),
    (OK, 'OK'),
]


class CountryReference(Model):
    """
    Справочник государств
    """
    class Meta:
        verbose_name = 'государство'
        verbose_name_plural = 'государства'

    name = CharField('название', max_length=50)

    def __str__(self):
        return self.name


class Account(AbstractUser):
    """
    Учетная запись пользователя
    Дополнительные атрибуты нужны для корректного заполнения протоколов ВОШ и Туймаады
    """
    class Meta:
        verbose_name = 'пользователь'
        verbose_name_plural = 'пользователи'

    patronymic_name = CharField('отчество', max_length=50, blank=True, default='')
    birthday = DateField('дата рождения', blank=True, null=True)
    country = ForeignKey('CountryReference', on_delete=CASCADE, blank=True, null=True, verbose_name='гражданство')

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
    Всероссийская олимпиада школьников по информатике. Региональный этап. 9 класс.

    Флаг personal_rules включает правила личного зачета
    Флаг command_rules включает правила командного зачёта
    Флаги personal_rules и command_rules можно включать одновременно для проведения лично-командной олимпиады

    Если флаг active снят, то доступ к олимпиаде разрешен только для организаторов (пользователей с флагом staff)

    Флаг anonymous_access разрешает гостевой доступ к условиям задач и опубликованным результатам

    Участники могут читать условия после времени начала

    Участники могут отправлять решения между временем начала и времено окончания

    Если время заморозки задано между временем начала и временем окончания, тогда
    участники и анонимные пользователи могут видеть таблицу результатов во время олимпиады

    Если задано время публикации результатов участники и гости смогут видеть результаты после этого времени

    Флаг show_tests разрешает участникам и гостям видеть тесты после окончания олимпиады

    """
    class Meta:
        verbose_name = 'олимпиада'
        verbose_name_plural = 'олимпиады'
        ordering = ['brief_name']

    brief_name = CharField('краткое наименование', max_length=100)
    full_name = TextField('полное наименование')
    description = TextField('описание')
    active = BooleanField('активность')
    start = DateTimeField('время начала')
    stop = DateTimeField('время завершения', blank=True, null=True)
    freeze = DateTimeField('время заморозки результатов', blank=True, null=True)
    show_results = DateTimeField('время публикации результатов', blank=True, null=True)
    conditions = CharField('путь к файлу с условиями', max_length=255)
    rules = CharField('путь к файлу с правилами', max_length=255)
    personal_rules = BooleanField('использовать правила личного зачета')
    command_rules = BooleanField('использовать правила командного зачета')
    show_tests = BooleanField('публиковать тесты')
    anonymous_access = BooleanField('доступ без авторизации')
    registration_enabled = BooleanField('разрешить регистрацию пользователей')

    def __str__(self):
        return self.brief_name


class Problem(Model):
    """
    Задача
    """
    class Meta:
        verbose_name = 'задача'
        verbose_name_plural = 'задачи'
        ordering = ['name']

    name = CharField('название', max_length=100)
    conditions = TextField('текст условия в формате TeX', blank=True)
    input = CharField('входной файл', max_length=100)
    output = CharField('выходной файл', max_length=100)
    solutions = TextField('текст разбора в формате TeX', blank=True)
    checker = TextField('чекер', blank=True)
    checker_lang = ForeignKey('multimeter.Language', on_delete=CASCADE, verbose_name='язык программирования')
    author = ForeignKey('multimeter.Account', on_delete=CASCADE, verbose_name='автор')

    def __str__(self):
        return self.name


class ContestProblem(Model):
    """
    Код задачи в контесте
    """
    class Meta:
        verbose_name = 'код задачи в олимпиаде'
        verbose_name_plural = 'коды задач в олимпиаде'
        ordering = ['contest', 'code']

    code = CharField('код', max_length=10)
    contest = ForeignKey('multimeter.Contest', on_delete=CASCADE, verbose_name='олимпиада')
    problem = ForeignKey('multimeter.Problem', on_delete=CASCADE, verbose_name='задача')

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
    class Meta:
        verbose_name = 'подзадача'
        verbose_name_plural = 'подзадачи'
        ordering = ['problem', 'number']

    PARTIAL = 'PRT'
    ENTIRE = 'ENT'

    SCORING = [
        (PARTIAL, 'за каждый тест',),
        (ENTIRE, 'за подзадачу в целом',),
    ]

    FULL = 'FUL'
    BRIEF = 'BRF'

    RESULTS = [
        (FULL, 'за каждый тест',),
        (BRIEF, 'за подзадачу в целом',),
    ]

    problem = ForeignKey('multimeter.Problem', verbose_name='задача', on_delete=CASCADE)
    number = IntegerField('номер по порядку')
    scoring = CharField('начисление баллов', max_length=3, choices=SCORING)
    results = CharField('отображение результатов', max_length=3, choices=RESULTS)

    def __str__(self):
        return 'задача "%s", подзадача %s' % (
            self.problem,
            self.number,
        )


class AbstractTest(Model):
    class Meta:
        abstract = True

    number = IntegerField('номер по порядку')
    input = TextField('входные данные')
    output = TextField('выходные данные')


class Sample(AbstractTest):
    """
    Пример к задаче
    """
    class Meta:
        verbose_name = 'пример'
        verbose_name_plural = 'примеры'
        ordering = ['problem', 'number']

    problem = ForeignKey('multimeter.Problem', on_delete=CASCADE, verbose_name='задача')
    required = BooleanField('обязателен при проверке', default=False)

    def __str__(self):
        return 'задача "%s", пример %s' % (
            self.problem,
            self.number,
        )


class Test(AbstractTest):
    """
    Тест в подзадаче
    """
    class Meta:
        verbose_name = 'тест'
        verbose_name_plural = 'тесты'
        ordering = ['sub_task', 'number']

    sub_task = ForeignKey('multimeter.SubTask', on_delete=CASCADE, verbose_name='подзадача')

    def __str__(self):
        return '%s, тест %s' % (
            self.sub_task,
            self.number,
        )


class Submission(Model):
    """
    Отправка попытки решения на проверку
    """
    class Meta:
        verbose_name = 'подзадача'
        verbose_name_plural = 'подзадачи'
        ordering = ['number']

    contest_problem = ForeignKey('multimeter.ContestProblem', on_delete=CASCADE, verbose_name='задача')
    user = ForeignKey('multimeter.Account', on_delete=CASCADE)
    language = ForeignKey('multimeter.Language', on_delete=CASCADE, verbose_name='язык программирования')
    number = IntegerField('номер попытки')
    moment = DateTimeField('дата и время отправки')
    source = TextField('текст решения')

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
    class Meta:
        verbose_name = 'язык программирования'
        verbose_name_plural = 'языки программирования'
        ordering = ['name']

    name = CharField('название', max_length=100)
    compilation = TextField('строки компиляции')
    execution = TextField('строка выполнения')

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
    compilation_result = CharField('результат компиляции', max_length=2, choices=COMPILATION_RESULTS)
    score = IntegerField('баллы')


class TestResult(Model):
    """
    Результат проверки на тесте
    """
    class Meta:
        abstract = True
        verbose_name = 'результат проверки на тесте'
        verbose_name_plural = 'результаты проверок на тестах'

    check = ForeignKey('multimeter.Check', on_delete=CASCADE, verbose_name='проверка')
    test = ForeignKey('multimeter.AbstractTest', on_delete=CASCADE, verbose_name='тест')
    execution_result = CharField('результат выполнения', max_length=2, choices=EXECUTION_RESULTS)
    execution_output = TextField('вывод решения')
    execution_code = IntegerField('код возврата решения')
    check_output = IntegerField('вывод чекера')
    check_code = IntegerField('код возврата чекера')
    memory = IntegerField('память (кб)')
    time = IntegerField('время (кб)')
