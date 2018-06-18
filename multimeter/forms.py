""" Multimeter forms """

from django.core.exceptions import ValidationError
from django.forms import Form, ModelForm, CharField, PasswordInput
from django.forms import ChoiceField, EmailField, FileField, HiddenInput

from multimeter.models import Account, Problem


class LoginForm(Form):
    """ Форма входа в систему """
    username = CharField(max_length=150, label='Логин')
    password = CharField(widget=PasswordInput(), label='Пароль')


class SignupForm(ModelForm):
    """ Форма регистрации """
    password = CharField(widget=PasswordInput())
    email = EmailField(label='Адрес электронной почты')

    class Meta:
        model = Account
        fields = ['username', 'password', 'first_name', 'last_name', 'patronymic_name', 'email']


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
    tags = CharField(max_length=200, label='Теги', required=False)

    class Meta:
        exclude = []
        model = Problem
        widgets = {'author': HiddenInput}


class ImportProblemForm(Form):
    """ Форма импорта задачи из Polygon """
    file = FileField(label='Файл', required=True)
    language = ChoiceField(label='Предпочтительный язык', choices=(
        ('russian', 'Русский'), ('english', 'English')
    ))
