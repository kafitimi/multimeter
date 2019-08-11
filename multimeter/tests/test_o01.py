""" Тест по карточке O-01 Редактирование контеста
Организатор контеста может создать и редактировать контест. Обязательными реквизитами контеста являются
* полное название;
* краткое название;
* дата и время начала;
* дата и время окончания;
* выбор правил зачета (личный, командный, лично-командный)
"""
import datetime

from django.test import TestCase
from django.urls import reverse
from django.utils.translation import gettext as _

from multimeter.models import Account, Contest


class TestO01(TestCase):
    """ Тестирование редактирования контеста """

    def setUp(self):
        self.admin = Account()
        self.admin.is_superuser = True
        self.admin.username = 'admin'
        self.admin.set_password('password')
        self.admin.save()

        self.contest1 = Contest()
        self.contest1.owner = self.admin
        self.contest1.brief_name = "Олимпиада"
        self.contest1.start = datetime.datetime(2000, 1, 1, 12, 0, tzinfo=datetime.timezone.utc)
        self.contest1.stop = datetime.datetime(2000, 1, 1, 18, 0, tzinfo=datetime.timezone.utc)
        self.contest1.save()

    def test_contest_list(self):
        self.client.login(username='admin', password='password')

        response = self.client.get(reverse('contest_list'))
        self.assertEqual(200, response.status_code)
        self.assertContains(response, _('Contest list'))
        self.assertContains(response, _('Create'))
        self.assertContains(response, self.contest1.brief_name)

    def test_contest_create(self):
        self.client.login(username='admin', password='password')

        response = self.client.get(reverse('contest_create'))
        self.assertEqual(200, response.status_code)
        self.assertContains(response, _('Save'))

    def test_contest_update(self):
        self.client.login(username='admin', password='password')

        response = self.client.get(reverse('contest_update', kwargs={'pk': self.contest1.pk}))
        self.assertEqual(200, response.status_code)
        self.assertContains(response, self.contest1.brief_name)
        self.assertContains(response, _('Save'))

    def test_contest_delete(self):
        self.client.login(username='admin', password='password')

        response = self.client.get(reverse('contest_delete', kwargs={'pk': self.contest1.pk}))
        self.assertEqual(200, response.status_code)
        self.assertContains(response, self.contest1.brief_name)
        self.assertContains(response, _('Delete'))
