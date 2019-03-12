import json
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.core import serializers
from .models import User, LastUpdate


def showGsocUser(request):
    sort = 'd'
    if 'sort' in request.GET:
        sort = request.GET['sort']
    updated = LastUpdate.objects.filter(pk=1)
    if updated:
        lastUpdated = updated.update
    else:
        lastUpdated = ''
    users = sortUser(User.objects.filter(gsoc=True), sort)
    data = serializers.serialize('json', list(users), fields=(
        'login', 'id', 'avatar', 'gsoc', 'totalOpenPRs', 'totalMergedPRs', 'totalIssues'))
    context = {
        'users': json.loads(data),
        'updated': lastUpdated,
    }
    return render(request, 'core/gsoclist.html', context)

def sortUser(_User, key):
    if key == 'm':
        return _User.order_by('-totalMergedPRs')
    elif key == 'p':
        return _User.order_by('-totalOpenPRs')
    elif key == 'i':
        return _User.order_by('-totalIssues')
    else: # defalut case for gsoc
        return User.objects.filter(gsoc=True).extra(
        select={'count':'totalMergedPRs + totalOpenPRs'},
        order_by=('-count',),
        )
