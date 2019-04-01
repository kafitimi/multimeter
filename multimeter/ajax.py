from .models import Account, Contest
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponseNotFound, HttpResponse, QueryDict
import json


def account_list(request):
    if request.is_ajax() and request.method == 'POST':
        payload = json.loads(request.body)
        filters = payload.get('include', dict())
        exclusion_filters = payload.get('exclude', dict())
        accounts = Account.objects.exclude(**exclusion_filters).filter(**filters)
        return render(request, 'multimeter/account_list.html', {'accounts': accounts})
    else:
        return HttpResponseNotFound()


@user_passes_test(lambda u: u.is_staff)
def update_contest_participants(request, pk):
    if request.is_ajax() and request.method == 'PUT':
        payload = QueryDict(request.body)
        participants = payload.getlist('ids[]')
        contest = get_object_or_404(Contest, pk=pk)
        contest.account_set.set(participants)
        return HttpResponse(status=204)
    else:
        return HttpResponseNotFound()
