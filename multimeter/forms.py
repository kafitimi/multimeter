from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.forms import Form, CharField, TextInput, PasswordInput, DateField, ModelForm, DateInput

from multimeter.models import Attribute, ParticipantCharValue, Account, ParticipantDateValue


class LoginForm(Form):
    """ Форма входа в систему """
    username = CharField(max_length=25, widget=TextInput(), label='Логин')
    password = CharField(max_length=25, widget=PasswordInput(), label='Пароль')


class PasswordForm(Form):
    """ Форма изменения пароля """
    current_password = CharField(max_length=30, widget=PasswordInput(), label='Текущий пароль')
    new_password = CharField(max_length=30, widget=PasswordInput(), label='Новый пароль')
    confirm_password = CharField(max_length=30, widget=PasswordInput(), label='Подтверждение нового пароля')

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


class AccountForm(Form):
    """ Форма редактирования пользователем учетной записи """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['username'] = CharField(label='Логин', max_length=150)
        self.fields['first_name'] = CharField(label='Имя', max_length=30)
        self.fields['last_name'] = CharField(label='Фамилия', max_length=150)

        for attr in Attribute.objects.all():
            model = attr.attr_type.model_class()
            if model == ParticipantCharValue:
                self.fields[attr.identifier] = CharField(max_length=100, label=attr.name)
            elif model == ParticipantDateValue:
                self.fields[attr.identifier] = DateField(label=attr.name)

    def load_account(self, account):
        self.initial = {
            'username': account.username,
            'first_name': account.first_name,
            'last_name': account.last_name
        }
        for attr in Attribute.objects.all():
            model = attr.attr_type.model_class()
            if not model is None:
                try:
                    self.initial[attr.identifier] = model.objects.get(account=account, attribute=attr).value
                except ObjectDoesNotExist:
                    pass

    def save(self, account):
        account.username = self.data['username']
        account.first_name = self.data['first_name']
        account.last_name = self.data['last_name']
        account.save()

        for attr in Attribute.objects.all():
            model = attr.attr_type.model_class()
            if not model is None:
                try:
                    instance = model.objects.get(account=account, attribute=attr)
                except ObjectDoesNotExist:
                    instance = model()
                    instance.account = account
                    instance.attribute = attr
                instance.value = self.data[attr.identifier]
                instance.save()
