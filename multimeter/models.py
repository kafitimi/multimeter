from django.db import models
from django.contrib.auth.models import AbstractUser


class Account(AbstractUser):

    def __str__(self):
        return self.username


class Attribute(models.Model):
    name = models.CharField(max_length=30)
    mandatory = models.BooleanField()


class AccountCharAttribute(models.Model):
    account = models.ForeignKey('Account', on_delete=models.CASCADE)
    attribute = models.ForeignKey('Attribute', on_delete=models.CASCADE)
    value = models.CharField(max_length=100)

    class Meta:
        unique_together = (('account', 'attribute'),)


class Contest(models.Model):
    class Meta:
        verbose_name = 'олимпиада'
        verbose_name_plural = 'олимпиады'

    brief_name = models.CharField('краткое наименование', max_length=100, default='')
    full_name = models.TextField('полное наименование', default='')
    description = models.TextField('описание', default='')
    active = models.BooleanField('активность', default=False)
    start = models.DateTimeField('дата и время начала', default='')
    stop = models.DateTimeField('дата и время завершения', default='')
    conditions = models.CharField('путь к файлу с условиями', max_length=255, default='')
    rules = models.CharField('путь к файлу с правилами', max_length=255, default='')
    individual = models.BooleanField('личный зачет', default=False)
    command = models.BooleanField('командный зачет', default=False)


class Problem(models.Model):
    class Meta:
        verbose_name = 'задача'
        verbose_name_plural = 'задачи'

    code = models.CharField('код', max_length=10, default='')
    name = models.CharField('наименование', max_length=100, default='')
    contest = models.ForeignKey('multimeter.Contest', verbose_name='олимпиада', on_delete=models.CASCADE)
    conditions = models.TextField('текст условия', default='')
    input = models.CharField('входной файл', max_length=100, default='')
    output = models.CharField('выходной файл', max_length=100, default='')


class Example(models.Model):
    class Meta:
        verbose_name = 'пример'
        verbose_name_plural = 'примеры'

    problem = models.ForeignKey('multimeter.Problem', verbose_name='задача', on_delete=models.CASCADE)
    order = models.IntegerField('номер по порядку', default=0)
    input = models.TextField('входные данные', default='')
    output = models.TextField('выходные', default='')
