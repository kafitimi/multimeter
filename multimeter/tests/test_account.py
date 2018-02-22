""" Модульный тест для проверки работы учётных записей """
from django.test import TestCase, Client

from multimeter import models


class TestAccount(TestCase):
    """ Тестирование представлений (views) учетной записи """

    def setUp(self):
        admin = models.Account()
        admin.is_superuser = True
        admin.username = 'admin'
        admin.set_password('right')
        admin.save()

    def test_login_page(self):
        """ Тест страницы авторизации """
        client = Client()

        # Неавторизованный пользователь
        response = client.get('/')
        self.assertRedirects(response, '/login/?next=/')

        # Страница входа
        response = client.get('/login/')
        self.assertTemplateUsed(response, 'multimeter/login.html')

        # Неправильный логин
        response = client.post('/login/', {'username': 'wrong', 'password': 'right'})
        self.assertContains(response, 'Неправильный логин или пароль', status_code=200)

        # Неправильный пароль
        response = client.post('/login/', {'username': 'admin', 'password': 'wrong'})
        self.assertContains(response, 'Неправильный логин или пароль', status_code=200)

        # Правильный логин и пароль
        response = client.post('/login/', {'username': 'admin', 'password': 'right'})
        self.assertRedirects(response, '/')

    def test_logout(self):
        """ Тест страницы выхода из системы """
        client = Client()
        client.login(username='admin', password='right')

        response = client.get('/logout/')
        self.assertRedirects(response, '/login/')

    def test_account_page(self):
        """ Тест страницы редактирования учетной записи """
        client = Client()
        client.login(username='admin', password='right')

        # Открытие профиля пользоватея /account/ => страница страница профиля без новых данных
        response = client.get('/account/')
        self.assertContains(response, 'Профиль пользователя', status_code=200)
        self.assertNotContains(response, 'John', status_code=200)
        self.assertNotContains(response, 'Doe', status_code=200)
        self.assertNotContains(response, 'Jay', status_code=200)
        self.assertNotContains(response, '31.12.2000', status_code=200)

        # Отправка данных пользователя без необязательных полей => успех
        response = client.post('/account/', {
            'username': 'admin',
            'first_name': 'John',
            'last_name': 'Doe',
            'birthday': '31.12.2000',
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['location'], '/')

        # Открытие профиля пользоватея /account/ => страница страница профиля с новыми данными
        response = client.get('/account/')
        self.assertContains(response, 'John', status_code=200)
        self.assertContains(response, 'Doe', status_code=200)
        self.assertContains(response, '31.12.2000', status_code=200)

        # Очистка необязательных полей пользователя => перенаправление на главную страницу
        response = client.post('/account/', {
            'username': 'admin',
            'first_name': '',
            'last_name': '',
            'second_name': '',
            'birthday': '31.12.2000',
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['location'], '/')

        # Открытие профиля => страница страница не должна содержать очищенных данных
        response = client.get('/account/')
        self.assertNotContains(response, 'John', status_code=200)
        self.assertNotContains(response, 'Doe', status_code=200)
        self.assertNotContains(response, 'Jay', status_code=200)
