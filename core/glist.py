import json
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.core import serializers
from .models import User, LastUpdate
from .views import sortUser


def showGsocUser(request):
    sort = 'd'
    if 'sort' in request.GET:
        sort = request.GET['sort']
    if LastUpdate.objects.filter(pk=1):
        lastUpdated = LastUpdate.objects.get(pk=1).gList
    else:
        lastUpdated = ''
    users = sortUser(User.objects.filter(gsoc=True), sort, _gsoc = True)
    data = serializers.serialize('json', list(users), fields=(
        'login', 'id', 'avatar', 'gsoc', 'totalOpenPRs', 'totalMergedPRs', 'totalIssues'))
    context = {
        'users': json.loads(data),
        'updated': lastUpdated,
    }
    return render(request, 'core/gsoclist.html', context)
