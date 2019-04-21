""" Multimeter views """

from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.utils.decorators import method_decorator
from django.views.generic import ListView, DeleteView, CreateView, UpdateView
from django.http import HttpResponseForbidden, HttpResponseNotFound, HttpResponseNotAllowed

from multimeter.auth import login, signup
from multimeter.forms import (LoginForm, AccountForm, PasswordForm, ProblemForm, SignupForm,
                              ImportProblemForm, ProblemStatementsForm)
from multimeter.models import (Account, Contest, Problem, SubTask, ProblemText, DEFAULT_PROBLEM_TEXT_LANGUAGE,
                               PROBLEM_TEXT_LANGUAGES)
from multimeter import polygon


def login_page(request):
    """ Страница входа в систему """
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = login(request, form.cleaned_data)
            if user is None:
                form.add_error(None, 'Неправильный логин или пароль')
            else:
                return redirect('index')
    else:
        form = LoginForm()
    return render(request, 'multimeter/login.html', {'login_form': form})


def index_page(request):
    """ Главная страница """
    """ TODO proper open_contests filter"""
    if request.user.is_authenticated:
        user_contests = Account.objects.get(pk=request.user.id).participations.all()
    else:
        user_contests = []
    context = {
        'open_contests': Contest.objects.filter(participant_access=True).exclude(pk__in=user_contests),
        'user_contests': user_contests
    }
    return render(request, 'multimeter/index.html', context)


@login_required
def account_page(request):
    """ Настройки учетной записи """
    if request.method == 'POST':
        form = AccountForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('index')
    else:
        form = AccountForm(instance=request.user)
    return render(request, 'multimeter/account_form.html', {'form': form})


@login_required
def password_page(request):
    """ Страница изменения пароля """
    if request.method == 'POST':
        form = PasswordForm(request.POST)
        form.user = request.user
        if form.is_valid():
            form.user.set_password(form.cleaned_data['new_password'])
            form.user.save()
            update_session_auth_hash(request, form.user)
            return redirect('index')
    else:
        form = PasswordForm()
    return render(request, 'multimeter/password_change.html', {'form': form})


@method_decorator(user_passes_test(lambda u: u.is_superuser), name='dispatch')
class ContestList(ListView):
    """ Список контестов """
    model = Contest


@method_decorator(user_passes_test(lambda u: u.is_superuser), name='dispatch')
class ContestCreate(CreateView):
    """ Создание контеста """
    model = Contest
    fields = [
        'brief_name', 'full_name', 'statements', 'rules',
        'start', 'stop', 'freeze',
        'personal_rules', 'command_rules',
        'guest_access', 'participant_access',
        'show_tests', 'show_results', 'owner'
    ]
    success_url = reverse_lazy('contest_list')


@method_decorator(user_passes_test(lambda u: u.is_superuser), name='dispatch')
class ContestUpdate(UpdateView):
    """ Редактирование контеста """
    model = Contest
    fields = [
        'brief_name', 'full_name', 'statements', 'rules',
        'start', 'stop', 'freeze',
        'personal_rules', 'command_rules',
        'guest_access', 'participant_access',
        'show_tests', 'show_results',
    ]
    success_url = reverse_lazy('contest_list')


@method_decorator(user_passes_test(lambda u: u.is_superuser), name='dispatch')
class ContestDelete(DeleteView):
    """ Удаление контеста """
    model = Contest
    success_url = reverse_lazy('contest_list')


@user_passes_test(lambda u: u.is_staff)
def problem_list_page(request):
    """ Список задач """
    problem_list = Problem.objects.filter(author=request.user)
    return render(request, 'multimeter/problem_list.html', {'object_list': problem_list})


@user_passes_test(lambda u: u.is_staff)
def problem_edit_page(request, problem_id=None):
    """ Страница создания / редактирования задачи """
    problem = None if problem_id is None else get_object_or_404(Problem, pk=problem_id)
    initial = {
        'author': request.user if problem is None else problem.author,
        'tags': '' if problem is None else ','.join([t.tag for t in problem.tags.all()])
    }
    if request.method == 'POST':
        form = ProblemForm(request.POST, instance=problem)
        if form.is_valid():
            problem = form.save()
            problem.set_tags_from_string(form.cleaned_data['tags'])
            return redirect('problem_list')
    else:
        form = ProblemForm(initial=initial, instance=problem)
        statements_languages = set() if problem is None else problem.get_statement_languages()
        context = {
            'form': form,
            'problem': problem,
            'statements_languages': statements_languages,
            'statements_to_add': set(PROBLEM_TEXT_LANGUAGES) - statements_languages
        }
        return render(request, 'multimeter/problem_form.html', context)


class SignupFormView(CreateView):
    """ Форма регистрации """
    form_class = SignupForm
    template_name = 'multimeter/signup.html'

    def get(self, request, *args, **kwargs):
        """ метод GET протокола HTTP """
        form = self.form_class(None)
        return render(request, self.template_name, {'signup_form': form})

    def post(self, request, *args, **kwargs):
        """ метод GET протокола HTTP """
        form = self.form_class(request.POST)
        if form.is_valid():
            if signup(request, form.cleaned_data) is not None:
                return redirect('index')
            else:
                form.add_error(None, "Логин и(или) адрес электронной почты уже заняты")
        return render(request, self.template_name, {'signup_form': form})


@method_decorator(user_passes_test(lambda u: u.is_staff), name='dispatch')
class ProblemDelete(DeleteView):
    """ Удаление задачи """
    model = Problem
    success_url = reverse_lazy('problem_list')


@method_decorator(user_passes_test(lambda u: u.is_staff), name='dispatch')
class SubTaskCreate(CreateView):
    """ Создание подзадачи """
    model = SubTask
    fields = [
        'problem', 'number', 'scoring', 'results'
    ]
    success_url = reverse_lazy('problem_list')


@method_decorator(user_passes_test(lambda u: u.is_staff), name='dispatch')
class SubTaskUpdate(UpdateView):
    """ Редактирование подзадачи """
    model = SubTask
    fields = [
        'problem', 'number', 'scoring', 'results'
    ]
    success_url = reverse_lazy('problem_list')


@method_decorator(user_passes_test(lambda u: u.is_staff), name='dispatch')
class SubTaskDelete(DeleteView):
    """ Удаление подзадачи """
    model = SubTask
    success_url = reverse_lazy('problem_list')


@user_passes_test(lambda u: u.is_staff)
def problem_import(request):
    """ Импорт задачи из Polygon """
    if request.method == 'POST':
        form = ImportProblemForm(request.POST, request.FILES)
        if form.is_valid():
            language = form.cleaned_data.get('language')
            problems = polygon.process_archive(request.FILES['file'].file, language)
            for problem in problems:
                problem.problem.author = request.user
                problem.problem.save()
                problem.problem.set_tags(problem.tags)
        return render(request, 'multimeter/problem_import_result.html', {'object_list': problems})
    else:
        form = ImportProblemForm()
    return render(request, 'multimeter/problem_import.html', {'form': form})


def contest_join_page(request, contest_pk=None):
    contest = get_object_or_404(Contest, pk=contest_pk)
    """ TODO proper open_contests filter"""
    if not contest.participant_access:
        return HttpResponseForbidden()
    login_form = LoginForm(request.POST or None)
    signup_form = SignupForm(request.POST or None)
    if request.method == 'POST':
        user = request.user if request.user.is_authenticated else None
        if 'submit-login' in request.POST:
            if login_form.is_valid():
                user = login(request, login_form.cleaned_data)
                if user is None:
                    login_form.add_error(None, 'Неправильный логин или пароль')
        elif 'submit-signup' in request.POST:
            if signup_form.is_valid():
                user = signup(request, signup_form.cleaned_data)
                if user is None:
                    signup_form.add_error(None, 'Логин и(или) адрес электронной почты уже заняты')
        if user is not None:
            request.user.participations.add(contest)
            request.user.save()
            return redirect('index')
    context = {
        'contest': contest,
        'login_form': login_form,
        'signup_form': signup_form,
        'is_login': 'submit-login' in request.POST,
    }
    return render(request, 'multimeter/contest_join.html', context)


@user_passes_test(lambda u: u.is_staff)
def problem_statements_form_page(request, pk, lang):
    problem = get_object_or_404(Problem, pk=pk)
    if request.method == 'POST':
        form = ProblemStatementsForm(request.POST)
        if form.is_valid():
            problem.set_statements(lang, form.map_to_text_types())
            return redirect('problem_update', problem_id=pk)
    elif request.method == 'GET':
        data = {}
        for name, _type in ProblemStatementsForm.FIELD_NAME_TO_TEXT_TYPE:
            try:
                text = problem.problemtext_set.get(language=lang, text_type=_type)
                data[name] = text.text
            except ProblemText.DoesNotExist:
                data[name] = ''
        form = ProblemStatementsForm(data)
        context = {
            'problem_id': pk,
            'lang': lang,
            'form': form
        }
        return render(request, 'multimeter/problem_statements_form.html', context)
    else:
        return HttpResponseNotAllowed()


def problem_statements_delete_page(request, pk, lang):
    problem = get_object_or_404(Problem, pk=pk)
    if request.method == 'POST':
        problem.get_statements(lang).delete()
        return redirect('problem_update', problem_id=pk)
    else:
        context = {
            'lang': lang,
            'problem': problem
        }
        return render(request, 'multimeter/problem_statements_confirm_delete.html', context)



def contest_participants_edit_page(request, pk):
    if request.method == 'GET':
        contest = get_object_or_404(Contest, pk=pk)
        context = {
            'contest': contest
        }
        return render(request, 'multimeter/contest_participants_list.html', context)
    else:
        return HttpResponseNotFound()
