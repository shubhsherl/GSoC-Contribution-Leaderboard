import json
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.core import serializers
from .models import User, Glist
from .views import sortUser

def showGsocUser(request):
    sort = 'c'
    if 'sort' in request.GET:
        sort = request.GET['sort']
    users = sortUser(User.objects.filter(gsoc=True), sort)
    data = serializers.serialize('json', list(users), fields=('login','id', 'avatar', 'totalCommits', 'gsoc', 'totalAdd', 'totalDelete', 'totalPRs', 'totalIssues'))
    # update Glist{if admin added any member}
    for user in json.loads(data):
        if not Glist.objects.filter(login = user['fields']['login']):
            newUser = Glist(login = user['fields']['login'])
            newUser.save()
    context = {
        'users': json.loads(data),
    }
    return render(request, 'core/gsoclist.html', context)