""" Multimeter views """
from django.contrib.auth import authenticate, login, update_session_auth_hash
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import ListView, DeleteView, CreateView, UpdateView

from .forms import LoginForm, AccountForm, PasswordForm
from . import models


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


@login_required
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
    return render(request, 'multimeter/edit.html', {
        'caption': 'Профиль пользователя',
        'cancel_url': reverse('index'),
        'form': form
    })


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
    return render(request, 'multimeter/edit.html', {
        'caption': 'Изменение пароля',
        'cancel_url': reverse('index'),
        'form': form
    })


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


@method_decorator(user_passes_test(lambda u: u.is_staff), name='dispatch')  # pylint: disable=too-many-ancestors
class TaskList(ListView):
    """ Список задач """
    model = models.Task


@method_decorator(user_passes_test(lambda u: u.is_staff), name='dispatch')  # pylint: disable=too-many-ancestors
class TaskCreate(CreateView):
    """ Создание задачи """
    model = models.Task
    fields = [
        'name', 'conditions', 'input', 'output', 'solutions', 'checker', 'checker_lang', 'author',
    ]
    success_url = reverse_lazy('problem_list')


@method_decorator(user_passes_test(lambda u: u.is_staff), name='dispatch')  # pylint: disable=too-many-ancestors
class TaskUpdate(UpdateView):
    """ Редактирование задачи """
    model = models.Task
    fields = [
        'name', 'conditions', 'input', 'output', 'solutions', 'checker', 'checker_lang', 'author',
    ]
    success_url = reverse_lazy('task_list')


@method_decorator(user_passes_test(lambda u: u.is_staff), name='dispatch')  # pylint: disable=too-many-ancestors
class TaskDelete(DeleteView):
    """ Удаление задачи """
    model = models.Task
    success_url = reverse_lazy('task_list')


@method_decorator(user_passes_test(lambda u: u.is_staff), name='dispatch')  # pylint: disable=too-many-ancestors
class SubTaskCreate(CreateView):
    """ Создание подзадачи """
    model = models.SubTask
    fields = [
        'task', 'number', 'scoring', 'results'
    ]
    success_url = reverse_lazy('task_list')

@method_decorator(user_passes_test(lambda u: u.is_staff), name='dispatch')  # pylint: disable=too-many-ancestors
class SubTaskUpdate(UpdateView):
    """ Редактирование подзадачи """
    model = models.SubTask
    fields = [
        'task', 'number', 'scoring', 'results'
    ]
    success_url = reverse_lazy('task_list')


@method_decorator(user_passes_test(lambda u: u.is_staff), name='dispatch')  # pylint: disable=too-many-ancestors
class SubTaskDelete(DeleteView):
    """ Удаление подзадачи """
    model = models.SubTask
    success_url = reverse_lazy('task_list')
