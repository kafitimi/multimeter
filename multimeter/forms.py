import json
from datetime import date, datetime
from json import JSONDecodeError

from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.forms import Form, CharField, PasswordInput, DateField, ModelForm, HiddenInput

from multimeter.models import Attribute, Account


class LoginForm(Form):
    """ Форма входа в систему """
    username = CharField(max_length=150, label='Логин')
    password = CharField(widget=PasswordInput(), label='Пароль')


class PasswordForm(Form):
    """ Форма изменения пароля """
    current_password = CharField(widget=PasswordInput(), label='Текущий пароль')
    new_password = CharField(widget=PasswordInput(), label='Новый пароль')
    confirm_password = CharField(widget=PasswordInput(), label='Подтверждение нового пароля')

    def clean_current_password(self):
        current_password = self.cleaned_data['current_password']
        if not self.user.check_password(current_password):
            raise ValidationError('Неверный текущий пароль')
        return current_password

    def clean_confirm_password(self):
        confirm_password = self.cleaned_data['confirm_password']
        if confirm_password != self.cleaned_data['new_password']:
            raise ValidationError('Пароли не совпадают')
        return confirm_password


class AccountForm(ModelForm):
    class Meta:
        model = Account
        fields = ['username', 'first_name', 'last_name', 'attributes']
        labels = {
            'username': 'Логин',
            'first_name': 'Имя',
            'last_name': 'Фамилия',
        }
        widgets = {
            'attributes': HiddenInput()
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        attributes = {}
        try:
            attributes = json.loads(self.instance.attributes)
        except JSONDecodeError:
            pass

        for attr in Attribute.objects.all():
            if attr.data_type == Attribute.DATE:
                self.fields[attr.identifier] = DateField(required=attr.required, label=attr.name)
                date_value = attributes.get(attr.identifier, date(1, 1, 1))
                self.initial[attr.identifier] = datetime.strftime(date_value, '%d.%m.%Y')
            else:
                self.fields[attr.identifier] = CharField(max_length=100, required=attr.required, label=attr.name)
                self.initial[attr.identifier] = attributes.get(attr.identifier, '')

    def save(self, *args, **kwargs):
        # kwargs['commit'] = False
        attributes = {}
        for attr in Attribute.objects.all():
            if attr.data_type == Attribute.DATE:
                str_value = self.cleaned_data[attr.identifier]
                try:
                    attributes[attr.identifier] = datetime.strptime(str_value, '%d.%m.%Y').date()
                except ValueError:
                    pass
            else:
                attributes[attr.identifier] = self.cleaned_data[attr.identifier]
        self.cleaned_data['attributes'] = json.dumps(attributes)
        print(self.cleaned_data)
        # instance.save()
        # instance = \
        super().save(*args, **kwargs)

    # def clean(self):
    #     for attr in Attribute.objects.all():
    #         if attr.required and self.cleaned_data.get(attr.identifier, '') == '':
    #             raise ValidationError('Не заполнено обязательное поле')


class RegisterForm(Form):
    username = CharField(max_length=150, label='Логин')
    password = CharField(widget=PasswordInput(), label='Пароль')
    first_name = CharField(max_length=30, required=False, label='Имя')
    last_name = CharField(max_length=150, required=False, label='Фамилия')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # for attr in Attribute.objects.all():
        #     model = attr.attr_type.model_class()
        #     if model == AccountValueChar:
        #         self.fields[attr.identifier] = CharField(max_length=100, required=attr.required, label=attr.name)
        #     elif model == AccountValueDate:
        #         self.fields[attr.identifier] = DateField(required=attr.required, label=attr.name)

    def clean_username(self):
        username = self.cleaned_data['username']
        try:
            Account.objects.get(username=username)
            raise ValidationError('Пользователь с таким именем уже существует')
        except ObjectDoesNotExist:
            pass
        return username

    def clean(self):
        pass
        # for attr in Attribute.objects.all():
        #     if attr.identifier in self.cleaned_data:
        #         model = attr.attr_type.model_class()
        #         if model == AccountValueDate:
        #             try:
        #                 datetime.strftime(self.cleaned_data[attr.identifier], '%d.%m.%Y')
        #             except ValueError:
        #                 raise ValidationError('Дата должна быть отформатирована 25.01.2001')
