from django.contrib.auth import authenticate, login, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from multimeter.forms import LoginForm, PasswordForm, AccountForm, RegisterForm
from multimeter.models import Account


def login_view(request):
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


def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = Account()
            user.update(form.cleaned_data)
            user = authenticate(**form.cleaned_data)
            if user is not None:
                login(request, user)
                return redirect('index')
    else:
        form = RegisterForm()
    return render(request, 'multimeter/register.html', {'form': form})


@login_required
def password_view(request):
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
    return render(request, 'multimeter/password.html', {'form': form})


@login_required
def account_view(request):
    """ Настройки учетной записи """
    if request.method == 'POST':
        form = AccountForm(request.POST, instance=request.user)
        # form.load_account(request.user)
        if form.is_valid():
            # request.user.update(form.data)
            form.save()
            return redirect('index')
    else:
        form = AccountForm(instance=request.user)
        # form.load_account(request.user)
    return render(request, 'multimeter/account.html', {'form': form})


@login_required
def index_view(request):
    return render(request, 'multimeter/index.html', {})
