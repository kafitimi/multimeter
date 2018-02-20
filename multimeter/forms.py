""" Multimeter forms """
from django.core.exceptions import ValidationError
from django.forms import Form, CharField, PasswordInput, ModelForm

from multimeter.models import Account, Problem


class LoginForm(Form):
    """ Форма входа в систему """
    username = CharField(max_length=150, label='Логин')
    password = CharField(widget=PasswordInput(), label='Пароль')


class AccountForm(ModelForm):
    """ Форма настроек учетной записи пользователя """
    class Meta:
        model = Account
        fields = ['username', 'first_name', 'last_name', 'patronymic_name', 'birthday', 'country']
        labels = {'username': 'Логин'}


class PasswordForm(Form):
    """ Форма изменения пароля """
    current_password = CharField(widget=PasswordInput(), label='Текущий пароль')
    new_password = CharField(widget=PasswordInput(), label='Новый пароль')
    confirm_password = CharField(widget=PasswordInput(), label='Подтверждение нового пароля')

    def clean_current_password(self):
        """ Валидация текущего пароля """
        current_password = self.cleaned_data['current_password']
        if not self.user.check_password(current_password):
            raise ValidationError('Неверный текущий пароль')
        return current_password

    def clean_confirm_password(self):
        """ Валидация подтверждения пароля """
        confirm_password = self.cleaned_data['confirm_password']
        if confirm_password != self.cleaned_data['new_password']:
            raise ValidationError('Пароли не совпадают')
        return confirm_password


class ProblemForm(ModelForm):
    """ Форма редактирования задачи """
    class Meta:
        model = Problem
        fields = [
            'name', 'conditions', 'input', 'output', 'solutions', 'checker', 'checker_lang',
            'author'
        ]
