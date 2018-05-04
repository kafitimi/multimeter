""" Multimeter views """
from django.contrib.auth import authenticate, login, update_session_auth_hash
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import ListView, DeleteView, CreateView, UpdateView

from multimeter.forms import LoginForm, AccountForm, PasswordForm, ProblemForm, SignupForm, ImportProblemForm
from multimeter.models import Problem, Account
from multimeter import models
import multimeter.polygon
from multimeter.polygon import ImportResult


def login_page(request):
    """ Страница входа в систему """
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(**form.cleaned_data)
            if user is None:
                form.add_error(None, 'Неправильный логин или пароль')
            else:
                login(request, user)
                return redirect('index')
    else:
        form = LoginForm()
    return render(request, 'multimeter/login.html', {'form': form})


def index_page(request):
    """ Главная страница """
    return render(request, 'multimeter/index.html', {})


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


@method_decorator(user_passes_test(lambda u: u.is_superuser), name='dispatch')  # pylint: disable=too-many-ancestors
class ContestList(ListView):
    """ Список контестов """
    model = models.Contest


@method_decorator(user_passes_test(lambda u: u.is_superuser), name='dispatch')  # pylint: disable=too-many-ancestors
class ContestCreate(CreateView):
    """ Создание контеста """
    model = models.Contest
    fields = [
        'brief_name', 'full_name', 'conditions', 'rules',
        'start', 'stop', 'freeze',
        'personal_rules', 'command_rules',
        'guest_access', 'participant_access',
        'show_tests', 'show_results',
    ]
    success_url = reverse_lazy('contest_list')


@method_decorator(user_passes_test(lambda u: u.is_superuser), name='dispatch')  # pylint: disable=too-many-ancestors
class ContestUpdate(UpdateView):
    """ Редактирование контеста """
    model = models.Contest
    fields = [
        'brief_name', 'full_name', 'conditions', 'rules',
        'start', 'stop', 'freeze',
        'personal_rules', 'command_rules',
        'guest_access', 'participant_access',
        'show_tests', 'show_results',
    ]
    success_url = reverse_lazy('contest_list')


@method_decorator(user_passes_test(lambda u: u.is_superuser), name='dispatch')  # pylint: disable=too-many-ancestors
class ContestDelete(DeleteView):
    """ Удаление контеста """
    model = models.Contest
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
        'tags': '' if problem is None else ' '.join([t.tag for t in problem.tags.all()])
    }
    if request.method == 'POST':
        form = ProblemForm(request.POST, instance=problem)
        if form.is_valid():
            problem = form.save()
            problem.set_tags(form.cleaned_data['tags'])
            return redirect('problem_list')
    else:
        form = ProblemForm(initial=initial, instance=problem)
    return render(request, 'multimeter/problem_form.html', {'form': form, 'problem': problem})


class SignupFormView(CreateView):
    form_class = SignupForm
    template_name = 'multimeter/signup.html'

    def get(self, request):
        form = self.form_class(None)
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            email = form.cleaned_data['email']
            if not (Account.objects.filter(username=username).exists() or Account.objects.filter(email=email).exists()):
                user = form.save(commit=False)
                user.set_password(password)
                user.save()
                user = authenticate(username=username, password=password)
                login(request, user)
                return redirect('index')
            else:
                form.add_error(None, "Логин и(или) адрес электронной почты уже заняты")
        return render(request, self.template_name, {'form': form})


@method_decorator(user_passes_test(lambda u: u.is_staff), name='dispatch')  # pylint: disable=too-many-ancestors
class ProblemDelete(DeleteView):
    """ Удаление задачи """
    model = models.Problem
    success_url = reverse_lazy('problem_list')


@method_decorator(user_passes_test(lambda u: u.is_staff), name='dispatch')  # pylint: disable=too-many-ancestors
class SubTaskCreate(CreateView):
    """ Создание подзадачи """
    model = models.SubTask
    fields = [
        'problem', 'number', 'scoring', 'results'
    ]
    success_url = reverse_lazy('problem_list')

@method_decorator(user_passes_test(lambda u: u.is_staff), name='dispatch')  # pylint: disable=too-many-ancestors
class SubTaskUpdate(UpdateView):
    """ Редактирование подзадачи """
    model = models.SubTask
    fields = [
        'problem', 'number', 'scoring', 'results'
    ]
    success_url = reverse_lazy('problem_list')


@method_decorator(user_passes_test(lambda u: u.is_staff), name='dispatch')  # pylint: disable=too-many-ancestors
class SubTaskDelete(DeleteView):
    """ Удаление подзадачи """
    model = models.SubTask
    success_url = reverse_lazy('problem_list')


@user_passes_test(lambda u: u.is_staff)
def problem_import(request):
    if request.method == 'POST':
        form = ImportProblemForm(request.POST, request.FILES)
        if form.is_valid():
            problems = multimeter.polygon.process_archive(request.FILES['file'].file, form.cleaned_data.get('language'))
            results = []
            for p in problems:
                p.author = request.user
                p.save()
                results.append(ImportResult(p))
        return render(request, 'multimeter/problem_import_result.html', {'object_list': results})
    else:
        form = ImportProblemForm()
    return render(request, 'multimeter/problem_import.html', {'form': form})
