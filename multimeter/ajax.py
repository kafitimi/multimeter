from .models import Account
from django.shortcuts import render
from django.http import HttpResponseNotFound


def contest_participant_list(request):
    if request.is_ajax():
        if 'pk' in request.GET:
            accounts = Account.objects.filter(participations__in=[request.GET['pk']])
        else:
            accounts = []
        return render(request, 'multimeter/account_list.html', {'accounts': accounts})
    return HttpResponseNotFound()


def account_list_by_username(request):
    if request.is_ajax():
        accounts = Account.objects.filter(username__istartswith=request.GET.get('username.sw', default=''))
        return render(request, 'multimeter/account_list.html', {'accounts': accounts})
    return HttpResponseNotFound()
