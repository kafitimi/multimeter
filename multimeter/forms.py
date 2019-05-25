""" Multimeter forms """

from django.core.exceptions import ValidationError
from django.forms import Form, ModelForm, CharField, PasswordInput
from django.forms import ChoiceField, EmailField, FileField, HiddenInput, Textarea
from django.utils.translation import gettext_lazy as _

from multimeter.models import Account, Problem, ProblemText, Contest, ContestProblem, Submission


class LoginForm(Form):
    """ Форма входа в систему """
    username = CharField(max_length=150, label=_('username'))
    password = CharField(widget=PasswordInput(), label=_('password'))


class SignupForm(ModelForm):
    """ Форма регистрации """
    password = CharField(widget=PasswordInput(), label=_('password'))
    email = EmailField(label=_('email'))

    class Meta:
        model = Account
        fields = ['username', 'password', 'first_name', 'last_name', 'second_name', 'email']
        labels = {'second_name': _('second name')}


class AccountForm(ModelForm):
    """ Форма настроек учетной записи пользователя """
    class Meta:
        model = Account
        fields = ['username', 'first_name', 'last_name', 'second_name', 'birthday', 'country']
        labels = {'username': _('username')}


class PasswordForm(Form):
    """ Форма изменения пароля """
    current_password = CharField(widget=PasswordInput(), label=_('Current password'))
    new_password = CharField(widget=PasswordInput(), label=_('New password'))
    confirm_password = CharField(widget=PasswordInput(), label=_('Confirm new password'))

    def clean_current_password(self):
        """ Валидация текущего пароля """
        current_password = self.cleaned_data['current_password']
        if not self.user.check_password(current_password):
            raise ValidationError(_('Invalid current password'))
        return current_password

    def clean_confirm_password(self):
        """ Валидация подтверждения пароля """
        confirm_password = self.cleaned_data['confirm_password']
        if confirm_password != self.cleaned_data['new_password']:
            raise ValidationError(_('Passwords does not match'))
        return confirm_password


class ProblemForm(ModelForm):
    """ Форма редактирования задачи """
    tags = CharField(max_length=200, label=_('Tags'), help_text=_('Tags must be separated by commas'), required=False)

    class Meta:
        exclude = []
        model = Problem
        widgets = {'author': HiddenInput}


class ImportProblemForm(Form):
    """ Форма импорта задачи из Polygon """
    file = FileField(label=_('file'), required=True)
    language = ChoiceField(label=_('Preferred language'), choices=(
        ('russian', _('Russian')), ('english', _('English'))
    ))


class ProblemStatementsForm(Form):
    name = CharField(label=_('name'), required=False)
    legend = CharField(label=_('legend'), widget=Textarea, required=False)
    input_format = CharField(label=_('input format'), widget=Textarea, required=False)
    output_format = CharField(label=_('output format'), widget=Textarea, required=False)
    tutorial = CharField(label=_('tutorial'), widget=Textarea, required=False)

    FIELD_NAME_TO_TEXT_TYPE = (
        ('name', ProblemText.NAME),
        ('legend', ProblemText.LEGEND),
        ('input_format', ProblemText.INPUT_FORMAT),
        ('output_format', ProblemText.OUTPUT_FORMAT),
        ('tutorial', ProblemText.TUTORIAL)
    )

    def map_to_text_types(self):
        return {(_type, self.cleaned_data.get(name)) for (name, _type) in self.FIELD_NAME_TO_TEXT_TYPE}


class ContestForm(ModelForm):
    class Meta:
        model = Contest
        fields = [
            'brief_name', 'full_name', 'statements', 'rules',
            'start', 'stop', 'freeze',
            'personal_rules', 'command_rules',
            'guest_access', 'participant_access',
            'show_tests', 'show_results', 'problems'
        ]

    def save(self, commit=True):
        contest = super().save(commit=False)
        if commit:
            ContestProblem.objects.filter(contest=contest).delete()
            problems = self.data.getlist('problems')

            for index, problem_id in enumerate(problems):
                ContestProblem.objects.create(contest=contest, problem_id=problem_id, code=chr(97 + index))

            contest.save()
        return contest


class SubmissionForm(ModelForm):
    source_file = FileField(label=_('source'))

    class Meta:
        model = Submission
        fields = ['contest_problem', 'language']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in 'contest_problem', 'language':
            self.fields[field_name].empty_label = None
