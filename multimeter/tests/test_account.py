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

        # Неавторизованный пользователь
        response = self.client.get('/ru/')
        self.assertTemplateUsed(response, 'multimeter/index.html')

        # Страница входа
        response = self.client.get('/ru/login/')
        self.assertTemplateUsed(response, 'multimeter/login.html')

        # Неправильный логин
        response = self.client.post('/ru/login/', {'username': 'wrong', 'password': 'right'})
        self.assertContains(response, 'Неправильный логин или пароль', status_code=200)

        # Неправильный пароль
        response = self.client.post('/ru/login/', {'username': 'admin', 'password': 'wrong'})
        self.assertContains(response, 'Неправильный логин или пароль', status_code=200)

        # Правильный логин и пароль
        response = self.client.post('/ru/login/', {'username': 'admin', 'password': 'right'})
        self.assertRedirects(response, '/ru/')

    def test_logout(self):
        """ Тест страницы выхода из системы """
        self.client.login(username='admin', password='right')

        response = self.client.get('/ru/logout/')
        self.assertEqual(302, response.status_code)
        response = self.client.get(response.url)
        self.assertRedirects(response, '/en/login/')

    def test_account_page(self):
        """ Тест страницы редактирования учетной записи """
        self.client.login(username='admin', password='right')

        # Открытие профиля пользоватея /account/ => страница страница профиля без новых данных
        response = self.client.get('/ru/account/')
        self.assertContains(response, 'Профиль пользователя', status_code=200)
        self.assertNotContains(response, 'John', status_code=200)
        self.assertNotContains(response, 'Doe', status_code=200)
        self.assertNotContains(response, 'Jay', status_code=200)
        self.assertNotContains(response, '31.12.2000', status_code=200)

        # Отправка данных пользователя без необязательных полей => успех
        response = self.client.post('/ru/account/', {
            'username': 'admin',
            'first_name': 'John',
            'last_name': 'Doe',
            'birthday': '31.12.2000',
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['location'], '/ru/')

        # Открытие профиля пользоватея /account/ => страница страница профиля с новыми данными
        response = self.client.get('/ru/account/')
        self.assertContains(response, 'John', status_code=200)
        self.assertContains(response, 'Doe', status_code=200)
        self.assertContains(response, '31.12.2000', status_code=200)

        # Очистка необязательных полей пользователя => перенаправление на главную страницу
        response = self.client.post('/ru/account/', {
            'username': 'admin',
            'first_name': '',
            'last_name': '',
            'second_name': '',
            'birthday': '31.12.2000',
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['location'], '/ru/')

        # Открытие профиля => страница страница не должна содержать очищенных данных
        response = self.client.get('/ru/account/')
        self.assertNotContains(response, 'John', status_code=200)
        self.assertNotContains(response, 'Doe', status_code=200)
        self.assertNotContains(response, 'Jay', status_code=200)
