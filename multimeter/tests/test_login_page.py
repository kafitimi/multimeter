from django.test import TestCase, Client

from multimeter.models import Account


class TestAcc(TestCase):
    def setUp(self):
        # Тестовый пользователь
        admin = Account.objects.create(username='admin')
        admin.set_password('right password')
        admin.save()

    def test_account_view(self):
        # Авторизация
        c = Client()
        c.post('/login/', {'username': 'admin', 'password': 'right password'})

        # Открытие профиля пользоватея /account/ => страница страница профиля без новых данных
        r = c.get('/account/')
        self.assertContains(r, 'Профиль пользователя', status_code=200)
        self.assertNotContains(r, 'John', status_code=200)
        self.assertNotContains(r, 'Doe', status_code=200)
        self.assertNotContains(r, 'Jay', status_code=200)
        self.assertNotContains(r, '31.12.2000', status_code=200)

        # Отправка данных пользователя без обязательных полей => сообщение об ошибке
        r = c.post('/account/', {
            'username': 'admin',
            'first_name': 'John',
            'last_name': 'Doe',
            'second_name': 'Jay'
        })
        self.assertContains(r, 'Не заполнено обязательное поле', status_code=200)

        # Отправка данных пользователя без необязательных полей => перенаправление на главную страницу
        r = c.post('/account/', {
            'username': 'admin',
            'first_name': 'John',
            'last_name': 'Doe',
            'birthday': '31.12.2000',
        })
        self.assertEqual(r.status_code, 302)
        self.assertEqual(r['location'], '/')

        # Открытие профиля пользоватея /account/ => страница страница профиля с новыми данными
        r = c.get('/account/')
        self.assertContains(r, 'John', status_code=200)
        self.assertContains(r, 'Doe', status_code=200)
        self.assertContains(r, '31.12.2000', status_code=200)

        # Очистка необязательных полей пользователя => перенаправление на главную страницу
        r = c.post('/account/', {
            'username': 'admin',
            'first_name': '',
            'last_name': '',
            'second_name': '',
            'birthday': '31.12.2000',
        })
        self.assertEqual(r.status_code, 302)
        self.assertEqual(r['location'], '/')

        # Открытие профиля пользоватея /account/ => страница страница не должна содержать очищенных данных
        r = c.get('/account/')
        self.assertNotContains(r, 'John', status_code=200)
        self.assertNotContains(r, 'Doe', status_code=200)
        self.assertNotContains(r, 'Jay', status_code=200)
