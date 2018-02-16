from django.test import TestCase, Client

from multimeter import models


class TestAccount(TestCase):
    def setUp(self):
        admin = models.Account()
        admin.is_superuser = True
        admin.username = 'admin'
        admin.set_password('right')
        admin.save()

    def test_login_page(self):
        c = Client()

        # Неавторизованный пользователь
        r = c.get('/')
        self.assertRedirects(r, '/login/?next=/')

        # Страница входа
        r = c.get('/login/')
        self.assertTemplateUsed(r, 'multimeter/login.html')

        # Неправильный логин
        r = c.post('/login/', {'username': 'wrong', 'password': 'right'})
        self.assertContains(r, 'Неправильный логин или пароль', status_code=200)

        # Неправильный пароль
        r = c.post('/login/', {'username': 'admin', 'password': 'wrong'})
        self.assertContains(r, 'Неправильный логин или пароль', status_code=200)

        # Правильный логин и пароль
        r = c.post('/login/', {'username': 'admin', 'password': 'right'})
        self.assertRedirects(r, '/')

    def test_logout(self):
        c = Client()
        c.login(username='admin', password='right')

        r = c.get('/logout/')
        self.assertRedirects(r, '/login/')

    def test_account_page(self):
        c = Client()
        c.login(username='admin', password='right')

        r = c.get('/account/')
        self.assertContains(r, 'Профиль пользователя', status_code=200)
        self.assertNotContains(r, 'John', status_code=200)
        self.assertNotContains(r, 'Doe', status_code=200)
        self.assertNotContains(r, 'Jay', status_code=200)
        self.assertNotContains(r, '31.12.2000', status_code=200)

        r = c.post('/account/', {
            'username': 'admin',
            'first_name': 'John',
            'second_name': 'Jay',
            'last_name': 'Doe'
        })
        # self.assertTemplateUsed(r, 'multimeter/login.html')
