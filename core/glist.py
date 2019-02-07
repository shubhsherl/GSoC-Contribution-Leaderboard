import json
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.core import serializers
from .models import User
from .views import sortUser

def showGsocUser(request):
    sort = 'c'
    if 'sort' in request.GET:
        sort = request.GET['sort']
    users = sortUser(User.objects.filter(gsoc=True), sort)
    data = serializers.serialize('json', list(users), fields=('login','id', 'avatar', 'totalCommits', 'gsoc', 'totalAdd', 'totalDelete', 'totalPRs', 'totalIssues'))
    context = {
        'users': json.loads(data),
    }
    return render(request, 'core/gsoclist.html', context)