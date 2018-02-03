from django.test import TestCase, Client

from multimeter.models import Account, Attribute


class TestLoginView(TestCase):
    def setUp(self):
        # Тестовый пользователь
        admin = Account.objects.create(username='admin')
        admin.set_password('right password')
        admin.save()

        # Обязательный атрибут пользователя
        Attribute.objects.create(
            identifier='birthday',
            name='Birthday',
            number=1,
            required=True,
            data_type=Attribute.DATE,
        )

        # Необязательный атрибут пользователя
        Attribute.objects.create(
            identifier='second_name',
            name='Second name',
            number=2,
            required=False,
            data_type=Attribute.STRING,
        )

        self.client = Client()

    def test_login_view(self):
        # Просмотр главной страницы без авторизации => перенаправление на страницу входа
        response = self.client.get('/')
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response['location'].startswith('/login/'))

        # Открытие страницы входа /login/ => страница входа
        response = self.client.get('/login/')
        self.assertContains(response, 'Вход в систему', status_code=200)

        # Отправка неправильного логина => сообщение об ошибке
        response = self.client.post('/login/', {'username': 'wrong user', 'password': 'right password'})
        self.assertContains(response, 'Неправильный логин или пароль', status_code=200)

        # Отправка неправильного пароля => сообщение об ошибке
        response = self.client.post('/login/', {'username': 'admin', 'password': 'wrong password'})
        self.assertContains(response, 'Неправильный логин или пароль', status_code=200)

        # Отправка правильного пароля => перенаправление на главную страницу
        response = self.client.post('/login/', {'username': 'admin', 'password': 'right password'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['location'], '/')

        # Просмотр главной страницы после авторизации => главная страница
        response = self.client.get('/')
        self.assertContains(response, 'Главная страница', status_code=200)

    def test_logout_view(self):
        # Авторизация
        self.client.post('/login/', {'username': 'admin', 'password': 'right password'})

        # Открытие страницы выхода после авторизаци => перенаправление на страницу входа
        response = self.client.get('/logout/')
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response['location'].startswith('/login/'))

    def test_account_view(self):
        # Авторизация
        self.client.post('/login/', {'username': 'admin', 'password': 'right password'})

        # Открытие профиля пользоватея /account/ => страница страница профиля без новых данных
        response = self.client.get('/account/')
        self.assertContains(response, 'Профиль пользователя', status_code=200)
        self.assertNotContains(response, 'John', status_code=200)
        self.assertNotContains(response, 'Doe', status_code=200)
        self.assertNotContains(response, 'Jay', status_code=200)
        self.assertNotContains(response, '31.12.2000', status_code=200)

        # Отправка данных пользователя без обязательных полей => сообщение об ошибке
        response = self.client.post('/account/', {
            'username': 'admin',
            'first_name': 'John',
            'last_name': 'Doe',
            'second_name': 'Jay'
        })
        self.assertContains(response, 'Не заполнено обязательное поле', status_code=200)

        # Отправка данных пользователя без необязательных полей => перенаправление на главную страницу
        response = self.client.post('/account/', {
            'username': 'admin',
            'first_name': 'John',
            'last_name': 'Doe',
            'birthday': '31.12.2000',
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['location'], '/')

        # Открытие профиля пользоватея /account/ => страница страница профиля с новыми данными
        response = self.client.get('/account/')
        self.assertContains(response, 'John', status_code=200)
        self.assertContains(response, 'Doe', status_code=200)
        self.assertContains(response, '31.12.2000', status_code=200)

        # Очистка необязательных полей пользователя => перенаправление на главную страницу
        response = self.client.post('/account/', {
            'username': 'admin',
            'first_name': '',
            'last_name': '',
            'second_name': '',
            'birthday': '31.12.2000',
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['location'], '/')

        # Открытие профиля пользоватея /account/ => страница страница не должна содержать очищенных данных
        response = self.client.get('/account/')
        self.assertNotContains(response, 'John', status_code=200)
        self.assertNotContains(response, 'Doe', status_code=200)
        self.assertNotContains(response, 'Jay', status_code=200)
