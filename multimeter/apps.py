""" Настройки приложения """

from django.apps import AppConfig
from django.conf import settings
import os


class MultimeterConfig(AppConfig):
    """ Конфигурация приложения """
    name = 'multimeter'
    verbose_name = 'Мультиметр'

    def ready(self):
        try:
            os.mkdir(settings.SUBMISSION_QUEUE_DIR)
            print('Submission queue directory is missing. Creating one.')
        except FileExistsError:
            print('Submission queue directory already exists.')
