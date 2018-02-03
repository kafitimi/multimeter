from django.contrib.contenttypes.models import ContentType
from django.db.models import Model, BooleanField, CASCADE, CharField, IntegerField, ForeignKey, TextField, \
    DateTimeField
from django.contrib.auth.models import AbstractUser


class Account(AbstractUser):

    attributes = TextField('Атрибуты пользователя', blank=True)

    def __str__(self):
        return '%s %s (%s)' % (
            self.last_name,
            self.first_name,
            self.username,
        )

    def get_data(self):
        data = {
            'username': self.username,
            'first_name': self.first_name,
            'last_name': self.last_name
        }
        for ct in ContentType.objects.all():
            if ct.model.startswith('accountvalue'):
                for instance in ct.model_class.objects.filter(account=self).select_related('Attribute'):
                    data[instance.attribute.identifier] = instance.get_value()
        return data

    def update(self, data):
        account_attrs = ['username', 'first_name', 'last_name']
        for attr in account_attrs:
            if attr in data:
                self.__setattr__(attr, data[attr])
        if 'password' in data:
            self.set_password(data['password'])
        self.save()

        for attr in Attribute.objects.all():
            value = data.get(attr.identifier, '')
            if value != '':
                model_cls = attr.attr_type.model_class()
                model_cls.update(self, attr, value)


class Attribute(Model):
    class Meta:
        verbose_name = 'атрибут участника'
        verbose_name_plural = 'атрибуты участников'
        ordering = ['number']

    STRING = 'STR'
    DATE = 'DAT'

    DATA_TYPES = [
        (STRING, 'строка'),
        (DATE, 'дата'),
    ]

    number = IntegerField('номер по порядку')
    identifier = CharField('идентификатор', max_length=30)
    name = CharField('название', max_length=50)
    required = BooleanField('обязательный')
    data_type = CharField('Тип данных', max_length=3, choices=DATA_TYPES)


class Contest(Model):
    """
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

    def __str__(self):
        return self.brief_name

    brief_name = CharField('краткое наименование', max_length=100)
    full_name = TextField('полное наименование')
    description = TextField('описание')
    active = BooleanField('активность')
    start = DateTimeField('время начала')
    stop = DateTimeField('время завершения', blank=True)
    freeze = DateTimeField('время заморозки результатов', blank=True)
    show_results = DateTimeField('время публиковации результатов', blank=True)
    conditions = CharField('путь к файлу с условиями', max_length=255)
    rules = CharField('путь к файлу с правилами', max_length=255)
    personal_rules = BooleanField('личный зачет')
    command_rules = BooleanField('командный зачет')
    show_tests = BooleanField('публиковать тесты')
    anonymous_access = BooleanField('доступ без авторизации')
    registration_enabled = BooleanField('регистрация пользователей разрешена')


class Problem(Model):
    class Meta:
        verbose_name = 'задача'
        verbose_name_plural = 'задачи'
        ordering = ['name']

    def __str__(self):
        return self.name

    name = CharField('название', max_length=100)
    author = ForeignKey('multimeter.Account', verbose_name='автор', on_delete=CASCADE)
    conditions = TextField('текст условия в TeX')
    solutions = TextField('текст разбора в TeX')
    input = CharField('входной файл', max_length=100)
    output = CharField('выходной файл', max_length=100)
    checker = TextField('чекер')


class ContestProblem(Model):
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

    code = CharField('код', max_length=10)
    contest = ForeignKey('multimeter.Contest', verbose_name='олимпиада', on_delete=CASCADE)
    problem = ForeignKey('multimeter.Problem', verbose_name='задача', on_delete=CASCADE)


class Example(Model):
    class Meta:
        verbose_name = 'пример'
        verbose_name_plural = 'примеры'
        ordering = ['problem', 'number']

    def __str__(self):
        return 'задача "%s", пример %s' % (
            self.problem,
            self.number,
        )

    problem = ForeignKey('multimeter.Problem', verbose_name='задача', on_delete=CASCADE)
    number = IntegerField('номер по порядку')
    input = TextField('входные данные')
    output = TextField('выходные данные')


class SubTask(Model):
    class Meta:
        verbose_name = 'подзадача'
        verbose_name_plural = 'подзадачи'
        ordering = ['problem', 'number']

    def __str__(self):
        return 'задача "%s", подзадача %s' % (
            self.problem,
            self.number,
        )

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


class Test(Model):
    class Meta:
        verbose_name = 'тест'
        verbose_name_plural = 'тесты'
        ordering = ['sub_task', 'number']

    def __str__(self):
        return '%s, тест %s' % (
            self.sub_task,
            self.number,
        )

    sub_task = ForeignKey('multimeter.SubTask', verbose_name='подзадача', on_delete=CASCADE)
    number = IntegerField('номер по порядку')
    input = TextField('входные данные')
    output = TextField('выходные данные')


class Submission(Model):
    class Meta:
        verbose_name = 'подзадача'
        verbose_name_plural = 'подзадачи'
        ordering = ['number']

    def __str__(self):
        return '%s, пользователь %s, попытка %s' % (
            self.contest_problem,
            self.user,
            self.number,
        )

    contest_problem = ForeignKey('multimeter.ContestProblem', verbose_name='задача', on_delete=CASCADE)
    user = ForeignKey('multimeter.Account', on_delete=CASCADE)
    language = ForeignKey('multimeter.Language', on_delete=CASCADE, verbose_name='язык программирования')
    number = IntegerField('номер попытки')
    moment = DateTimeField('дата и время отправки')
    source = TextField('текст решения')


class Language(Model):
    class Meta:
        verbose_name = 'язык программирования'
        verbose_name_plural = 'языки программирования'
        ordering = ['name']

    def __str__(self):
        return self.name

    name = CharField('название', max_length=100)
    compilation = TextField('строки компиляции')
    execution = TextField('строка выполнения')


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


class Check(Model):
    """
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


class ExecutionResult(Model):
    class Meta:
        abstract = True
        verbose_name = 'результат проверки'
        verbose_name_plural = 'результаты проверки'

    check = ForeignKey('multimeter.Check', on_delete=CASCADE, verbose_name='проверка')
    execution_result = CharField('результат выполнения', max_length=2, choices=EXECUTION_RESULTS)


class ExampleResult(ExecutionResult):
    class Meta:
        abstract = True
        verbose_name = 'результат проверки на примере'
        verbose_name_plural = 'результаты проверок на примерах'

    subject = ForeignKey('multimeter.Example', on_delete=CASCADE, verbose_name='пример')


class TestResult(ExecutionResult):
    class Meta:
        abstract = True
        verbose_name = 'результат проверки на тесте'
        verbose_name_plural = 'результаты проверок на тестах'

    subject = ForeignKey('multimeter.Test', on_delete=CASCADE, verbose_name='тест')
